from django.db.models import Q

from inventory.models import Product


def get_filtered_products(request):
    products = Product.objects.select_related(
        "type",
        "texture",
        "storage_location",
        "created_by",
        "updated_by",
    )

    code_filter = request.GET.get("code", "").strip()
    name_filter = request.GET.get("name", "").strip()
    selected_type = request.GET.get("type", "")
    selected_texture = request.GET.get("texture", "")
    required_x = request.GET.get("dim_x", "").strip()
    required_y = request.GET.get("dim_y", "").strip()
    description_filter = request.GET.get("description", "").strip()
    selected_storage = request.GET.get("storage", "")
    price_filter = request.GET.get("price", "").strip()
    selected_status = request.GET.get("status", "")
    created_date = request.GET.get("created_date", "").strip()
    selected_created_by = request.GET.get("created_by", "")
    updated_date = request.GET.get("updated_date", "").strip()
    selected_updated_by = request.GET.get("updated_by", "")

    if code_filter:
        products = products.filter(
            code__icontains=code_filter,
        )

    if name_filter:
        products = products.filter(
            name__icontains=name_filter,
        )

    if selected_type:
        products = products.filter(
            type_id=selected_type,
        )

    if selected_texture:
        products = products.filter(
            texture_id=selected_texture,
        )

    try:
        dim_x = float(required_x) if required_x else None
    except ValueError:
        dim_x = None

    try:
        dim_y = float(required_y) if required_y else None
    except ValueError:
        dim_y = None

    if dim_x is not None and dim_y is not None:
        products = products.filter(
            Q(
                dimension_x__gte=dim_x,
                dimension_y__gte=dim_y,
            )
            | Q(
                dimension_x__gte=dim_y,
                dimension_y__gte=dim_x,
            )
        )
    elif dim_x is not None:
        products = products.filter(
            Q(dimension_x__gte=dim_x)
            | Q(dimension_y__gte=dim_x)
        )
    elif dim_y is not None:
        products = products.filter(
            Q(dimension_x__gte=dim_y)
            | Q(dimension_y__gte=dim_y)
        )

    if description_filter:
        products = products.filter(
            description__icontains=description_filter,
        )

    if selected_storage:
        products = products.filter(
            storage_location_id=selected_storage,
        )

    if price_filter:
        try:
            products = products.filter(
                price=float(price_filter),
            )
        except ValueError:
            pass

    if selected_status:
        products = products.filter(
            status=selected_status,
        )

    if created_date:
        products = products.filter(
            created_at__date=created_date,
        )

    if selected_created_by:
        products = products.filter(
            created_by_id=selected_created_by,
        )

    if updated_date:
        products = products.filter(
            updated_at__date=updated_date,
        )

    if selected_updated_by:
        products = products.filter(
            updated_by_id=selected_updated_by,
        )

    return products


def get_product_filter_context(request):
    return {
        "code_filter": request.GET.get("code", "").strip(),
        "name_filter": request.GET.get("name", "").strip(),
        "selected_type": request.GET.get("type", ""),
        "selected_texture": request.GET.get("texture", ""),
        "required_x": request.GET.get("dim_x", "").strip(),
        "required_y": request.GET.get("dim_y", "").strip(),
        "description_filter": request.GET.get("description", "").strip(),
        "selected_storage": request.GET.get("storage", ""),
        "price_filter": request.GET.get("price", "").strip(),
        "selected_status": request.GET.get("status", ""),
        "created_date": request.GET.get("created_date", "").strip(),
        "selected_created_by": request.GET.get("created_by", ""),
        "updated_date": request.GET.get("updated_date", "").strip(),
        "selected_updated_by": request.GET.get("updated_by", ""),
    }
