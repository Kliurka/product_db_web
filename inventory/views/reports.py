from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from weasyprint import HTML

from inventory.models import Order
from inventory.utils.permissions import role_required


@login_required
@role_required("admin", "manager")
def order_pdf(request, order_code):

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

    company = {
        "name": "UAB Akmens gaminiai",
        "company_code": "123456789",
        "vat_code": "LT123456789",
        "address": "Gatvė 1, Panevėžys, Lietuva",
        "phone": "+370 600 00000",
        "email": "info@example.lt",
        "website": "www.example.lt",
        "bank": "Swedbank",
        "iban": "LT00 0000 0000 0000 0000",
    }

    html_string = render_to_string(
        "inventory/pdf/order_pdf.html",
        {
            "company": company,
            "order": order,
            "items": items,
            "generated_at": timezone.localtime(),
        },
    )

    pdf_file = HTML(
        string=html_string,
        base_url=request.build_absolute_uri("/"),
    ).write_pdf()

    response = HttpResponse(
        pdf_file,
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        f'inline; filename="order-{order.order_code}.pdf"'
    )

    return response


@login_required
@role_required("admin", "manager", "worker")
def production_pdf(request, order_code):

    order = get_object_or_404(
        Order.objects.select_related(
            "customer",
        ),
        order_code=order_code,
    )

    items = (
        order.items
        .select_related("product")
        .all()
    )

    company = {
        "name": "STONE FACTORY",
    }

    html_string = render_to_string(
        "inventory/pdf/production_pdf.html",
        {
            "company": company,
            "order": order,
            "items": items,
        },
    )

    pdf = HTML(
        string=html_string,
        base_url=request.build_absolute_uri("/"),
    ).write_pdf()

    response = HttpResponse(
        pdf,
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        f'inline; filename="production-{order.order_code}.pdf"'
    )

    return response