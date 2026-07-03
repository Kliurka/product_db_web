from datetime import timezone
from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from inventory.forms import OrderForm, ProductForm
from inventory.models import (
    Discount,
    Order,
    OrderItem,
    Product,
    Reservation,
)
from inventory.utils.sorting import get_sort_params


# -------------------------
# Orders
# -------------------------
    
def order_list(request):
    orders = Order.objects.all()

    q = request.GET.get('q', '')
    payment_status = request.GET.get('payment_status', '')


    if q:
        orders = orders.filter(order_code__icontains=q) | Order.objects.filter(customer__name__icontains=q)

    if payment_status:
        orders = orders.filter(payment_status=payment_status)

    allowed_sort = ['order_code',
                    'customer__name',
                    'payment_status',
                    'partial_sum',
                    'created_at'
                    ]
    
    sort, direction, order_by = get_sort_params(
        request,
        'created_at',
        allowed_sort,
        'desc',
    )

    orders = orders.order_by(order_by)

    return render(request, 'inventory/order_list.html', {
        'orders': orders,
        'q': q,
        'payment_status': payment_status,
        'payment_statuses': Order.PAYMENT_STATUS,
        'sort': sort,
        'direction': direction,
    })

def create_order_item_and_reservation(order, product, discount_percent, tax_percent):
    unit_price = product.price or Decimal("0.00")
    quantity = Decimal("1.00")

    discount_percent = Decimal(str(discount_percent or 0))
    tax_percent = Decimal(str(tax_percent or 0))

    subtotal = unit_price * quantity
    discount_amount = subtotal * discount_percent / Decimal("100")
    taxable_sum = subtotal - discount_amount
    tax_amount = taxable_sum * tax_percent / Decimal("100")
    total = taxable_sum + tax_amount

    OrderItem.objects.create(
        order=order,
        product=product,
        product_code=product.code,
        product_name=product.name,
        quantity=quantity,
        unit_price=unit_price,
        discount_percent=discount_percent,
        tax_percent=tax_percent,
        subtotal=subtotal,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        total=total,
        created_at=timezone.now(),
    )

    Reservation.objects.create(
        order=order,
        product=product,
        reserved_at=timezone.now(),
        status='active'
    )

    product.status = 'reserved'
    product.updated_at = timezone.now()
    product.save()


def order_add(request):
    products = Product.objects.filter(status='available').order_by('code')

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)

            if order.partial_sum is None:
                order.partial_sum = 0

            order.created_at = timezone.now()
            order.updated_at = timezone.now()
            order.save()

            product_ids = request.POST.getlist('products')
            discounts = request.POST.getlist('line_discount')
            taxes = request.POST.getlist('line_tax')

            for index, product_id in enumerate(product_ids):
                product = Product.objects.get(id=product_id)

                discount_percent = discounts[index] if index < len(discounts) else 0
                tax_percent = taxes[index] if index < len(taxes) else 21

                create_order_item_and_reservation(
                    order,
                    product,
                    discount_percent,
                    tax_percent
                )

            order.partial_sum = sum(
                item.total for item in OrderItem.objects.filter(order=order)
            )
            order.save()

            return redirect('order_list')
    else:
        form = OrderForm()

    return render(request, 'inventory/order_form.html', {
        'form': form,
        'products': products,
        'mode': 'add',
    })

def product_edit(request, code):
    product = get_object_or_404(Product, code=code)

    if request.method == 'POST':
        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        'inventory/product_form.html',
        {
            'form': form,
            'mode': 'edit',
            'product': product,
        }
    )

def order_edit(request, order_code):
    order = get_object_or_404(Order, order_code=order_code)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)

        if form.is_valid():
            order = form.save(commit=False)
            order.updated_at = timezone.now()
            order.save()

            old_product_ids = list(
                Reservation.objects.filter(order=order, status='active')
                .values_list('product_id', flat=True)
            )

            for product_id in old_product_ids:
                Product.objects.filter(id=product_id).update(status='available')

            Reservation.objects.filter(order=order).delete()
            OrderItem.objects.filter(order=order).delete()

            product_ids = request.POST.getlist('products')
            discounts = request.POST.getlist('line_discount')
            taxes = request.POST.getlist('line_tax')

            for index, product_id in enumerate(product_ids):
                product = Product.objects.get(id=product_id)

                discount_percent = discounts[index] if index < len(discounts) else 0
                tax_percent = taxes[index] if index < len(taxes) else 21

                create_order_item_and_reservation(
                    order,
                    product,
                    discount_percent,
                    tax_percent
                )

            order.partial_sum = sum(
                item.total for item in OrderItem.objects.filter(order=order)
            )
            order.save()

            return redirect('order_list')

    else:
        form = OrderForm(instance=order)

    order_items = OrderItem.objects.filter(order=order).select_related('product')

    products = Product.objects.filter(status='available').order_by('code')

    return render(request, 'inventory/order_form.html', {
        'form': form,
        'mode': 'edit',
        'order': order,
        'products': products,
        'order_items': order_items,
    })
    