from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction


MONEY_STEP = Decimal("0.01")
PERCENT_DIVISOR = Decimal("100")


def money(value):
    """
    Suapvalina reikšmę iki 2 skaitmenų po kablelio.
    """
    if value is None:
        value = Decimal("0")

    return Decimal(value).quantize(
        MONEY_STEP,
        rounding=ROUND_HALF_UP,
    )


def calculate_order_item(item):
    """
    Perskaičiuoja vieną OrderItem pagal momentines jo reikšmes.

    Nenaudoja dabartinės Product kainos, Discount ar Tax lentelių,
    todėl seni užsakymai neperskaičiuojami pagal naujus tarifus.
    """
    quantity = Decimal(item.quantity or 0)
    unit_price = Decimal(item.unit_price or 0)
    discount_percent = Decimal(item.discount_percent or 0)
    tax_percent = Decimal(item.tax_percent or 0)

    subtotal = quantity * unit_price
    discount_amount = subtotal * discount_percent / PERCENT_DIVISOR
    taxable_amount = subtotal - discount_amount
    tax_amount = taxable_amount * tax_percent / PERCENT_DIVISOR
    total = taxable_amount + tax_amount

    item.subtotal = money(subtotal)
    item.discount_amount = money(discount_amount)
    item.tax_amount = money(tax_amount)
    item.total = money(total)

    return item


@transaction.atomic
def recalculate_order(order):
    """
    Perskaičiuoja visas užsakymo eilutes ir bendras Order sumas.
    """
    subtotal = Decimal("0")
    discount_total = Decimal("0")
    tax_total = Decimal("0")
    grand_total = Decimal("0")

    for item in order.items.select_for_update().all():
        calculate_order_item(item)

        item.save(
            update_fields=[
                "subtotal",
                "discount_amount",
                "tax_amount",
                "total",
            ]
        )

        subtotal += item.subtotal
        discount_total += item.discount_amount
        tax_total += item.tax_amount
        grand_total += item.total

    order.subtotal = money(subtotal)
    order.discount_total = money(discount_total)
    order.tax_total = money(tax_total)
    order.grand_total = money(grand_total)
    order.partial_sum = order.grand_total

    order.save(
        update_fields=[
            "subtotal",
            "discount_total",
            "tax_total",
            "grand_total",
            "partial_sum",
        ]
    )

    return order