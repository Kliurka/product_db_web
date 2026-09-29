from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from weasyprint import HTML

from inventory.models import Order
from inventory.utils.product_filters import get_filtered_products
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


PRODUCT_EXPORT_COLUMNS = [
    ("code", "Code", 16),
    ("name", "Name", 26),
    ("type", "Type", 18),
    ("texture", "Texture", 18),
    ("dimension_x", "Dim X", 12),
    ("dimension_y", "Dim Y", 12),
    ("description", "Description", 34),
    ("storage_location", "Storage Location", 18),
    ("price", "Price", 12),
    ("status", "Status", 14),
    ("created_at", "Created At", 18),
    ("created_by", "Created By", 16),
    ("updated_at", "Updated At", 18),
    ("updated_by", "Updated By", 16),
]


def _selected_product_export_columns(request):
    selected = request.GET.getlist("columns")
    valid_keys = {
        key
        for key, label, width in PRODUCT_EXPORT_COLUMNS
    }

    selected = [
        key
        for key in selected
        if key in valid_keys
    ]

    if not selected:
        selected = [
            key
            for key, label, width in PRODUCT_EXPORT_COLUMNS
        ]

    return [
        (key, label, width)
        for key, label, width in PRODUCT_EXPORT_COLUMNS
        if key in selected
    ]


def _product_export_value(product, key):
    if key == "code":
        return product.code

    if key == "name":
        return product.name

    if key == "type":
        return str(product.type or "")

    if key == "texture":
        return str(product.texture or "")

    if key == "dimension_x":
        return product.dimension_x

    if key == "dimension_y":
        return product.dimension_y

    if key == "description":
        return product.description or ""

    if key == "storage_location":
        return str(product.storage_location or "")

    if key == "price":
        return product.price

    if key == "status":
        return product.get_status_display()

    if key == "created_at":
        return (
            product.created_at.replace(tzinfo=None)
            if product.created_at
            else None
        )

    if key == "created_by":
        return str(product.created_by or "")

    if key == "updated_at":
        return (
            product.updated_at.replace(tzinfo=None)
            if product.updated_at
            else None
        )

    if key == "updated_by":
        return str(product.updated_by or "")

    return ""


@login_required
@role_required("admin", "manager", "worker", "viewer")
def product_list_excel(request):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter

    products = get_filtered_products(request).order_by("code")
    columns = _selected_product_export_columns(request)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Products"

    worksheet.append([
        label
        for key, label, width in columns
    ])

    for cell in worksheet[1]:
        cell.font = Font(bold=True)

    for product in products:
        worksheet.append([
            _product_export_value(product, key)
            for key, label, width in columns
        ])

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for index, column in enumerate(columns, start=1):
        key, label, width = column
        worksheet.column_dimensions[
            get_column_letter(index)
        ].width = width

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
    response["Content-Disposition"] = (
        'attachment; filename="filtered-products.xlsx"'
    )

    return response


@login_required
@role_required("admin", "manager", "worker", "viewer")
def product_list_pdf(request):
    products = list(
        get_filtered_products(request).order_by("code")
    )
    columns = _selected_product_export_columns(request)

    pdf_columns = [
        {
            "key": key,
            "label": label,
        }
        for key, label, width in columns
    ]

    rows = [
        [
            _product_export_value(product, key)
            for key, label, width in columns
        ]
        for product in products
    ]

    html_string = render_to_string(
        "inventory/pdf/product_list_pdf.html",
        {
            "columns": pdf_columns,
            "rows": rows,
            "product_count": len(products),
            "generated_at": timezone.localtime(),
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
        'inline; filename="filtered-products.pdf"'
    )

    return response
