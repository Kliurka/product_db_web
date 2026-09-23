from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from inventory.models import Order, OrderItem, OrderItemOperation, ProductionOperation
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
        .prefetch_related(
            "production_operations__operation",
        )
        .all()
    )

    available_operations = (
        ProductionOperation.objects
        .filter(active=True)
        .order_by("sort_order", "name")
    )

    return render(
        request,
        "inventory/production_detail.html",
        {
            "order": order,
            "items": items,
            "available_operations": available_operations,
        },
    )


@login_required
@role_required("admin", "manager", "worker")
@require_POST
def production_operation_add(request, order_code, item_id):
    order = get_object_or_404(
        Order,
        order_code=order_code,
    )

    item = get_object_or_404(
        OrderItem,
        pk=item_id,
        order=order,
    )

    operation = get_object_or_404(
        ProductionOperation,
        pk=request.POST.get("operation_id"),
        active=True,
    )

    OrderItemOperation.objects.get_or_create(
        order_item=item,
        operation=operation,
        defaults={
            "sort_order": operation.sort_order,
        },
    )

    return redirect(
        "production_detail",
        order_code=order.order_code,
    )


@login_required
@role_required("admin", "manager", "worker")
@require_POST
def production_operation_status(request, order_code, operation_id):
    item_operation = get_object_or_404(
        OrderItemOperation.objects.select_related(
            "order_item__order",
        ),
        pk=operation_id,
        order_item__order__order_code=order_code,
    )

    new_status = request.POST.get("status")

    valid_statuses = dict(
        OrderItemOperation.OPERATION_STATUS
    )

    if new_status not in valid_statuses:
        return redirect(
            "production_detail",
            order_code=order_code,
        )

    item_operation.status = new_status

    if new_status == "in_progress" and not item_operation.started_at:
        item_operation.started_at = timezone.now()

    if new_status == "completed":
        if not item_operation.started_at:
            item_operation.started_at = timezone.now()
        item_operation.completed_at = timezone.now()
    else:
        item_operation.completed_at = None

    item_operation.save(
        update_fields=[
            "status",
            "started_at",
            "completed_at",
        ]
    )

    return redirect(
        "production_detail",
        order_code=order_code,
    )


@login_required
@role_required("admin", "manager")
@require_POST
def production_operation_remove(request, order_code, operation_id):
    item_operation = get_object_or_404(
        OrderItemOperation,
        pk=operation_id,
        order_item__order__order_code=order_code,
    )

    item_operation.delete()

    return redirect(
        "production_detail",
        order_code=order_code,
    )
