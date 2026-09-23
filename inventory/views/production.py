from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from inventory.models import Order
from inventory.utils.permissions import role_required


@login_required
@role_required("admin", "manager", "worker")
def production_list(request):

    orders = (
        Order.objects
        .select_related("customer")
        .prefetch_related("items")
        .filter(
            status__in=[
                "confirmed",
                "in_production",
                "ready",
            ]
        )
        .order_by(
            "created_at",
        )
    )

    return render(
        request,
        "inventory/production_list.html",
        {
            "orders": orders,
        },
    )




@login_required
@role_required("admin", "manager", "worker")
def production_detail(request, order_code):

    order = get_object_or_404(
        Order.objects.select_related(
            "customer",
            "created_by",
            "updated_by",
        ),
        order_code=order_code,
    )

    items = (
        order.items
        .select_related("product")
        .all()
    )

    return render(
        request,
        "inventory/production_detail.html",
        {
            "order": order,
            "items": items,
        },
    )