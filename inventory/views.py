import qrcode
from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Product
from django.shortcuts import render

from .models import ProductType

from .forms import ProductForm
from django.shortcuts import redirect

from django.db.models import Sum
from .models import Order

from .forms import ProductForm, OrderForm
from .models import ProductType, Order, Product

from django.utils import timezone
from .models import Reservation

from django.shortcuts import get_object_or_404

from decimal import Decimal
from .models import OrderItem

from .models import Customer, AppUser
from .forms import CustomerForm, AppUserForm

from django.db.models import Count
from .models import Discount, Tax

from .models import StorageLocation
from .forms import StorageLocationForm

from .models import Texture
from .forms import TextureForm


def product_list(request):
    products = Product.objects.all()

    q = request.GET.get('q', '')
    selected_type = request.GET.get('type', '')
    selected_status = request.GET.get('status', '')
    sort = request.GET.get('sort', 'code')
    direction = request.GET.get('dir', 'asc')

    if q:
        products = products.filter(code__icontains=q) | Product.objects.filter(name__icontains=q)

    if selected_type:
        products = products.filter(type_id=selected_type)

    if selected_status:
        products = products.filter(status=selected_status)

    allowed_sort = [
        'code',
        'name',
        'type__name',
        'texture__name',
        'dimension_x',
        'dimension_y',
        'storage_location__sector',
        'price',
        'status',
        'created_at',
        'updated_at',
    ]

    if sort not in allowed_sort:
        sort = 'code'

    order_by = sort if direction == 'asc' else '-' + sort
    products = products.order_by(order_by)

    context = {
        'products': products,
        'types': ProductType.objects.all(),
        'statuses': Product.PRODUCT_STATUS,
        'q': q,
        'selected_type': selected_type,
        'selected_status': selected_status,
        'sort': sort,
        'direction': direction,
    }

    return render(request, 'inventory/product_list.html', context)

def product_qr(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    img = qrcode.make(product.qr_text())

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')



def product_detail(request, code):
    product = get_object_or_404(Product, code=code)

    return render(
        request,
        'inventory/product_detail.html',
        {'product': product}
    )


def scan_qr(request):
    return render(request, 'inventory/scan_qr.html')


def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save()
            return redirect('product_detail', code=product.code)
    else:
        form = ProductForm()

    return render(request, 'inventory/product_form.html', {
        'form': form,
        'mode': 'add',
    })
    
def order_list(request):
    orders = Order.objects.all()

    q = request.GET.get('q', '')
    payment_status = request.GET.get('payment_status', '')
    sort = request.GET.get('sort', 'created_at')
    direction = request.GET.get('dir', 'desc')

    if q:
        orders = orders.filter(order_code__icontains=q) | Order.objects.filter(customer__name__icontains=q)

    if payment_status:
        orders = orders.filter(payment_status=payment_status)

    allowed_sort = ['order_code', 'customer__name', 'payment_status', 'partial_sum', 'created_at']
    if sort not in allowed_sort:
        sort = 'created_at'

    order_by = sort if direction == 'asc' else '-' + sort
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
    

def customer_list(request):
    customers = Customer.objects.annotate(
        orders_count=Count('order')
    )

    q = request.GET.get('q', '')
    selected_discount = request.GET.get('discount', '')
    selected_tax = request.GET.get('tax', '')
    has_orders = request.GET.get('has_orders', '')
    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('dir', 'asc')

    if q:
        customers = customers.filter(name__icontains=q)

    if selected_discount:
        customers = customers.filter(discount_id=selected_discount)

    if selected_tax:
        customers = customers.filter(tax_id=selected_tax)

    if has_orders == 'yes':
        customers = customers.filter(orders_count__gt=0)

    if has_orders == 'no':
        customers = customers.filter(orders_count=0)

    allowed_sort = [
        'name',
        'phone',
        'email',
        'discount__percent',
        'tax__percent',
        'orders_count',
    ]

    if sort not in allowed_sort:
        sort = 'name'

    order_by = sort if direction == 'asc' else '-' + sort
    customers = customers.order_by(order_by)

    return render(request, 'inventory/customer_list.html', {
        'customers': customers,
        'q': q,
        'discounts': Discount.objects.all(),
        'taxes': Tax.objects.all(),
        'selected_discount': selected_discount,
        'selected_tax': selected_tax,
        'has_orders': has_orders,
        'sort': sort,
        'direction': direction,
    })


def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save()
            return redirect('customer_edit', customer_id=customer.id)
    else:
        form = CustomerForm()

    return render(request, 'inventory/customer_form.html', {
        'form': form,
        'mode': 'add',
    })


def customer_edit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)

        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'inventory/customer_form.html', {
        'form': form,
        'mode': 'edit',
        'customer': customer,
    })


def storage_list(request):
    storage_locations = StorageLocation.objects.all().order_by(
        'sector',
        'number',
        'position'
    )

    q = request.GET.get('q', '')

    if q:
        storage_locations = storage_locations.filter(
            sector__icontains=q
        ) | StorageLocation.objects.filter(
            number__icontains=q
        ) | StorageLocation.objects.filter(
            position__icontains=q
        ) | StorageLocation.objects.filter(
            description__icontains=q
        )

    return render(request, 'inventory/storage_list.html', {
        'storage_locations': storage_locations,
        'q': q,
    })


def storage_add(request):
    if request.method == 'POST':
        form = StorageLocationForm(request.POST)

        if form.is_valid():
            storage = form.save()
            return redirect('storage_edit', storage_id=storage.id)
    else:
        form = StorageLocationForm()

    return render(request, 'inventory/storage_form.html', {
        'form': form,
        'mode': 'add',
    })


def storage_edit(request, storage_id):
    storage = get_object_or_404(StorageLocation, id=storage_id)

    if request.method == 'POST':
        form = StorageLocationForm(request.POST, instance=storage)

        if form.is_valid():
            form.save()
            return redirect('storage_list')
    else:
        form = StorageLocationForm(instance=storage)

    return render(request, 'inventory/storage_form.html', {
        'form': form,
        'mode': 'edit',
        'storage': storage,
    })


def texture_list(request):
    textures = Texture.objects.all().order_by('name')

    q = request.GET.get('q', '')
    if q:
        textures = textures.filter(name__icontains=q)

    return render(request, 'inventory/texture_list.html', {
        'textures': textures,
        'q': q,
    })


def texture_add(request):
    if request.method == 'POST':
        form = TextureForm(request.POST)

        if form.is_valid():
            texture = form.save()
            return redirect('texture_edit', texture_id=texture.id)
    else:
        form = TextureForm()

    return render(request, 'inventory/texture_form.html', {
        'form': form,
        'mode': 'add',
    })


def texture_edit(request, texture_id):
    texture = get_object_or_404(Texture, id=texture_id)

    if request.method == 'POST':
        form = TextureForm(request.POST, instance=texture)

        if form.is_valid():
            form.save()
            return redirect('texture_list')
    else:
        form = TextureForm(instance=texture)

    return render(request, 'inventory/texture_form.html', {
        'form': form,
        'mode': 'edit',
        'texture': texture,
    })