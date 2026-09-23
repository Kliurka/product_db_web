from django.core.exceptions import ValidationError
from django.db import transaction

from inventory.models import Order


ORDER_TRANSITIONS = {
    "draft": {
        "confirmed",
        "cancelled",
    },
    "confirmed": {
        "in_production",
        "cancelled",
    },
    "in_production": {
        "ready",
        "cancelled",
    },
    "ready": {
        "delivered",
        "cancelled",
    },
    "delivered": {
        "completed",
    },
    "completed": set(),
    "cancelled": set(),
}


def get_allowed_transitions(order):
    return ORDER_TRANSITIONS.get(
        order.status,
        set(),
    )


def can_transition(order, new_status):
    return new_status in get_allowed_transitions(order)


@transaction.atomic
def change_order_status(order, new_status):
    locked_order = Order.objects.select_for_update().get(
        pk=order.pk,
    )

    if new_status not in dict(Order.ORDER_STATUS):
        raise ValidationError(
            "Unknown order status."
        )

    if not can_transition(locked_order, new_status):
        raise ValidationError(
            (
                f"Order cannot be changed from "
                f"'{locked_order.get_status_display()}' "
                f"to '{dict(Order.ORDER_STATUS)[new_status]}'."
            )
        )

    if (
        locked_order.status == "draft"
        and new_status == "confirmed"
        and not locked_order.items.exists()
    ):
        raise ValidationError(
            "An empty order cannot be confirmed."
        )

    locked_order.status = new_status
    locked_order.save(
        update_fields=[
            "status",
        ]
    )

    return locked_order