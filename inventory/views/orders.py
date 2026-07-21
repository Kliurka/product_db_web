from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib import messages


from inventory.forms import OrderForm
from inventory.models import (
    Order,
    OrderItem,
    Product,
    Reservation,
)
from inventory.utils.order_calculator import (
    calculate_order_item,
    recalculate_order,
)
from inventory.utils.permissions import role_required
from inventory.utils.sorting import get_sort_params
from inventory.forms import PaymentForm
from inventory.models import Order, Payment

# -------------------------
# Orders
# -------------------------


@login_required
@role_required("admin", "manager", "worker")
def order_list(request):
    orders = Order.objects.select_related("customer").all()

    q = request.GET.get("q", "").strip()
    payment_status = request.GET.get("payment_status", "")
    status = request.GET.get("status", "")

    if q:
        orders = orders.filter(
            Q(order_code__icontains=q)
            | Q(customer__name__icontains=q)
        )

    if payment_status:
        orders = orders.filter(payment_status=payment_status)

    if status:
        orders = orders.filter(status=status)

    allowed_sort = [
        "order_code",
        "customer__name",
        "status",
        "payment_status",
        "grand_total",
        "created_at",
    ]

    sort, direction, order_by = get_sort_params(
        request,
        "created_at",
        allowed_sort,
        "desc",
    )

    orders = orders.order_by(order_by)

    return render(
        request,
        "inventory/order_list.html",
        {
            "orders": orders,
            "q": q,
            "status": status,
            "payment_status": payment_status,
            "statuses": Order.ORDER_STATUS,
            "payment_statuses": Order.PAYMENT_STATUS,
            "sort": sort,
            "direction": direction,
        },
    )


def create_order_item_and_reservation(
    order,
    product,
    discount_percent,
    tax_percent,
):
    """
    Sukuria momentinę OrderItem kopiją ir rezervuoja produktą.

    Kaina, nuolaida ir mokestis nukopijuojami į OrderItem,
    todėl vėlesni Product, Discount ar Tax pakeitimai
    nepakeičia seno užsakymo.
    """
    unit_price = product.price or Decimal("0.00")
    quantity = Decimal("1.00")

    discount_percent = Decimal(str(discount_percent or 0))
    tax_percent = Decimal(str(tax_percent or 0))

    item = OrderItem(
        order=order,
        product=product,
        product_code=product.code,
        product_name=product.name,
        quantity=quantity,
        unit_price=unit_price,
        discount_percent=discount_percent,
        tax_percent=tax_percent,
        created_at=timezone.now(),
    )

    calculate_order_item(item)
    item.save()

    Reservation.objects.create(
        order=order,
        product=product,
        reserved_at=timezone.now(),
        status="active",
    )

    product.status = "reserved"
    product.updated_at = timezone.now()
    product.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return item


def release_order_products(order):
    """
    Atlaisvina visus aktyviai rezervuotus užsakymo produktus.
    """
    product_ids = list(
        Reservation.objects.filter(
            order=order,
            status="active",
        ).values_list(
            "product_id",
            flat=True,
        )
    )

    if product_ids:
        Product.objects.filter(
            id__in=product_ids,
        ).update(
            status="available",
            updated_at=timezone.now(),
        )


def get_selected_line_value(values, index, default):
    """
    Saugiai paima tos pačios eilutės reikšmę iš POST sąrašo.
    """
    if index >= len(values):
        return default

    value = values[index]

    if value in (None, ""):
        return default

    return value


@login_required
@role_required("admin", "manager")
@transaction.atomic
def order_add(request):
    products = Product.objects.filter(
        status="available",
    ).order_by("code")

    if request.method == "POST":
        form = OrderForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)

            if order.partial_sum is None:
                order.partial_sum = Decimal("0.00")

            order.created_at = timezone.now()
            order.updated_at = timezone.now()
            order.created_by = request.user.profile
            order.updated_by = request.user.profile
            order.save()

            product_ids = request.POST.getlist("products")
            discounts = request.POST.getlist("line_discount")
            taxes = request.POST.getlist("line_tax")

            for index, product_id in enumerate(product_ids):
                if not product_id:
                    continue

                product = get_object_or_404(
                    Product,
                    id=product_id,
                    status="available",
                )

                discount_percent = get_selected_line_value(
                    discounts,
                    index,
                    0,
                )

                tax_percent = get_selected_line_value(
                    taxes,
                    index,
                    21,
                )

                create_order_item_and_reservation(
                    order=order,
                    product=product,
                    discount_percent=discount_percent,
                    tax_percent=tax_percent,
                )

            recalculate_order(order)

            return redirect(
                "order_detail",
                order_code=order.order_code,
            )
    else:
        form = OrderForm()

    return render(
        request,
        "inventory/order_form.html",
        {
            "form": form,
            "products": products,
            "mode": "add",
        },
    )


@login_required
@role_required("admin", "manager", "worker")
def order_detail(request, order_code):
    order = get_object_or_404(
        Order.objects.select_related(
            "customer",
            "created_by",
            "updated_by",
        ),
        order_code=order_code,
    )

    items = order.items.select_related(
        "product",
    ).all()

    payments = order.payments.select_related(
        "created_by",
    ).all()

    return render(
        request,
        "inventory/order_detail.html",
        {
            "order": order,
            "items": items,
            "payments": payments,
        },
    )


@login_required
@role_required("admin", "manager")
@transaction.atomic
def order_edit(request, order_code):
    order = get_object_or_404(
        Order,
        order_code=order_code,
    )

    # Forma neturi keisti užsakymo sukūrimo datos.
    original_created_at = order.created_at

    current_product_ids = list(
        order.items.exclude(
            product_id=None,
        ).values_list(
            "product_id",
            flat=True,
        )
    )

    if request.method == "POST":
        form = OrderForm(
            request.POST,
            instance=order,
        )

        if form.is_valid():
            order = form.save(commit=False)

            order.updated_at = timezone.now()
            order.updated_by = request.user.profile

            order.save(
                update_fields=[
                    "order_code",
                    "customer",
                    "payment_status",
                    "partial_sum",
                    "description",
                    "updated_at",
                    "updated_by",
                ]
            )

            release_order_products(order)

            Reservation.objects.filter(
                order=order,
            ).delete()

            OrderItem.objects.filter(
                order=order,
            ).delete()

            product_ids = request.POST.getlist("products")
            discounts = request.POST.getlist("line_discount")
            taxes = request.POST.getlist("line_tax")

            for index, product_id in enumerate(product_ids):
                if not product_id:
                    continue

                product = get_object_or_404(
                    Product,
                    id=product_id,
                )

                if product.status != "available":
                    product_was_in_order = product.id in current_product_ids

                    if not product_was_in_order:
                        continue

                discount_percent = get_selected_line_value(
                    discounts,
                    index,
                    0,
                )

                tax_percent = get_selected_line_value(
                    taxes,
                    index,
                    21,
                )

                create_order_item_and_reservation(
                    order=order,
                    product=product,
                    discount_percent=discount_percent,
                    tax_percent=tax_percent,
                )

            recalculate_order(order)

            return redirect(
                "order_detail",
                order_code=order.order_code,
            )
    else:
        form = OrderForm(
            instance=order,
        )

    order_items = order.items.select_related(
        "product",
    ).all()

    products = Product.objects.filter(
        Q(status="available")
        | Q(id__in=current_product_ids)
    ).distinct().order_by("code")

    return render(
        request,
        "inventory/order_form.html",
        {
            "form": form,
            "mode": "edit",
            "order": order,
            "products": products,
            "order_items": order_items,
        },
    )
    
    
@login_required
@role_required("admin", "manager")
@transaction.atomic
def payment_add(request, order_code):
    order = get_object_or_404(
        Order,
        order_code=order_code,
    )

    if order.status == "cancelled":
        messages.error(
            request,
            "Payments cannot be added to a cancelled order.",
        )
        return redirect(
            "order_detail",
            order_code=order.order_code,
        )

    if request.method == "POST":
        form = PaymentForm(
            request.POST,
            order=order,
        )

        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order
            payment.created_by = request.user.profile
            payment.save()

            order.payment_status = order.calculated_payment_status
            order.save(
                update_fields=[
                    "payment_status",
                ]
            )

            messages.success(
                request,
                "Payment added successfully.",
            )

            return redirect(
                "order_detail",
                order_code=order.order_code,
            )
    else:
        form = PaymentForm(
            order=order,
            initial={
                "amount": order.remaining,
            },
        )

    return render(
        request,
        "inventory/payment_form.html",
        {
            "order": order,
            "form": form,
        },
    )
    
    
@login_required
@role_required("admin", "manager")
@transaction.atomic
def payment_delete(request, payment_id):
    payment = get_object_or_404(
        Payment.objects.select_related("order"),
        pk=payment_id,
    )

    order = payment.order

    if request.method == "POST":
        payment.delete()

        order.payment_status = order.calculated_payment_status
        order.save(
            update_fields=[
                "payment_status",
            ]
        )

        messages.success(
            request,
            "Payment deleted successfully.",
        )

    return redirect(
        "order_detail",
        order_code=order.order_code,
    )
    
    
