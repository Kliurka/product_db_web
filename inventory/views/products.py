from io import BytesIO

import qrcode
from django.utils import timezone

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from inventory.forms import ProductForm
from inventory.models import Product, ProductType, Texture
from inventory.utils.sorting import get_sort_params

from django.contrib.auth.decorators import login_required
from inventory.utils.permissions import role_required



@login_required
@role_required("admin", "manager", "worker", "viewer")
def product_list(request):
    products = Product.objects.select_related(
        "type",
        "texture",
        "storage_location",
    )

    q = request.GET.get("q", "").strip()
    selected_type = request.GET.get("type", "")
    selected_texture = request.GET.get("texture", "")
    selected_status = request.GET.get("status", "")
    required_x = request.GET.get("dim_x", "").strip()
    required_y = request.GET.get("dim_y", "").strip()

    if q:
        products = products.filter(
            Q(code__icontains=q)
            | Q(name__icontains=q)
        )

    if selected_type:
        products = products.filter(
            type_id=selected_type,
        )

    if selected_texture:
        products = products.filter(
            texture_id=selected_texture,
        )

    if selected_status:
        products = products.filter(
            status=selected_status,
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

    allowed_sort = [
        "code",
        "name",
        "type__name",
        "texture__name",
        "dimension_x",
        "dimension_y",
        "storage_location__sector",
        "price",
        "status",
        "created_at",
        "updated_at",
    ]

    sort, direction, order_by = get_sort_params(
        request,
        "code",
        allowed_sort,
    )

    products = products.order_by(order_by)

    context = {
        "products": products,
        "types": ProductType.objects.all().order_by("name"),
        "textures": Texture.objects.all().order_by("name"),
        "statuses": Product.PRODUCT_STATUS,
        "q": q,
        "selected_type": selected_type,
        "selected_texture": selected_texture,
        "selected_status": selected_status,
        "required_x": required_x,
        "required_y": required_y,
        "sort": sort,
        "direction": direction,
    }

    return render(
        request,
        "inventory/product_list.html",
        context,
    )


def product_qr(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    img = qrcode.make(product.qr_text())

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')

@login_required
@role_required("admin", "manager", "worker", "viewer")
def product_detail(request, code):
    product = get_object_or_404(Product, code=code)

    return render(
        request,
        'inventory/product_detail.html',
        {'product': product}
    )


def scan_qr(request):
    return render(request, 'inventory/scan_qr.html')


@login_required
@role_required("admin", "manager", "worker")
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)

            product.created_at = timezone.now()
            product.updated_at = timezone.now()
            product.created_by = request.user.profile
            product.updated_by = request.user.profile

            product.save()

            return redirect('product_detail', code=product.code)
        
    else:
        form = ProductForm()

    return render(request, 'inventory/product_form.html', {
        'form': form,
        'mode': 'add',
        'textures': Texture.objects.all(),
    })


@login_required
@role_required("admin", "manager", "worker")
def product_edit(request, code):
    product = get_object_or_404(Product, code=code)

    if request.method == 'POST':
        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():
            product = form.save(commit=False)

            product.updated_at = timezone.now()
            product.updated_by = request.user.profile

            product.save()

            return redirect('product_detail', code=product.code)

    else:
        form = ProductForm(instance=product)

    return render(
        request,
        'inventory/product_form.html',
        {
            'form': form,
            'mode': 'edit',
            'product': product,
            'textures': Texture.objects.all(),
            "photos": product.images.all(),
        }
    )