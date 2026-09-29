from io import BytesIO
import base64

import qrcode
from PIL import Image, ImageDraw
from django.utils import timezone

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from inventory.forms import ProductForm
from inventory.models import AppUser, Product, ProductType, StorageLocation, Texture
from inventory.utils.product_filters import get_filtered_products, get_product_filter_context
from inventory.utils.sorting import get_sort_params

from django.contrib.auth.decorators import login_required
from inventory.utils.permissions import role_required



@login_required
@role_required("admin", "manager", "worker", "viewer")
def product_list(request):
    products = get_filtered_products(request)

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

    users = (
        AppUser.objects
        .filter(active=True)
        .order_by("username")
    )

    context = {
        "products": products,
        "types": ProductType.objects.all().order_by("name"),
        "textures": Texture.objects.all().order_by("name"),
        "storage_locations": StorageLocation.objects.all().order_by(
            "sector",
            "number",
            "position",
        ),
        "users": users,
        "statuses": Product.PRODUCT_STATUS,
        "sort": sort,
        "direction": direction,
    }

    context.update(
        get_product_filter_context(request)
    )

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


@login_required
@role_required("admin", "manager", "worker", "viewer")
def scan_qr(request):
    code = request.GET.get("code", "").strip()

    if code:
        product = Product.objects.filter(
            code=code,
        ).first()

        if product:
            return redirect(
                "product_detail",
                code=product.code,
            )

        return render(
            request,
            "inventory/scan_qr.html",
            {
                "scan_error": (
                    f"Product with code '{code}' was not found."
                ),
                "scanned_code": code,
            },
        )

    return render(
        request,
        "inventory/scan_qr.html",
    )


def _product_qr_data_uri(product):
    image = qrcode.make(product.qr_text())

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    encoded = base64.b64encode(
        buffer.getvalue()
    ).decode("ascii")

    return f"data:image/png;base64,{encoded}"


@login_required
@role_required("admin", "manager", "worker", "viewer")
def product_labels(request):
    selected_ids = [
        value
        for value in request.GET.getlist("ids")
        if value.isdigit()
    ]

    if selected_ids:
        products = (
            Product.objects
            .select_related(
                "type",
                "texture",
                "storage_location",
            )
            .filter(id__in=selected_ids)
            .order_by("code")
        )
    else:
        products = get_filtered_products(
            request
        ).order_by("code")

    label_size = request.GET.get(
        "size",
        "60x40",
    )

    allowed_sizes = {
        "50x30": ("50mm", "30mm"),
        "60x40": ("60mm", "40mm"),
        "70x40": ("70mm", "40mm"),
    }

    if label_size not in allowed_sizes:
        label_size = "60x40"

    label_width, label_height = allowed_sizes[
        label_size
    ]

    label_products = [
        {
            "product": product,
            "qr_data_uri": _product_qr_data_uri(
                product
            ),
        }
        for product in products
    ]

    return render(
        request,
        "inventory/product_labels.html",
        {
            "label_products": label_products,
            "label_size": label_size,
            "label_width": label_width,
            "label_height": label_height,
        },
    )


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


@never_cache
def pwa_manifest(request):
    return JsonResponse(
        {
            "name": "Stone Factory ERP",
            "short_name": "Stone ERP",
            "description": "Stone Factory inventory and production ERP",
            "start_url": "/",
            "scope": "/",
            "display": "standalone",
            "background_color": "#f4f4ef",
            "theme_color": "#111111",
            "icons": [
                {
                    "src": "/pwa-icon/192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
                {
                    "src": "/pwa-icon/512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
            ],
        },
        content_type="application/manifest+json",
    )


@never_cache
def pwa_icon(request, size):
    if size not in (192, 512):
        size = 192

    image = Image.new(
        "RGB",
        (size, size),
        "#111111",
    )
    draw = ImageDraw.Draw(image)

    margin = int(size * 0.14)
    line_width = max(4, int(size * 0.035))

    top = (size // 2, int(size * 0.20))
    left = (int(size * 0.28), int(size * 0.31))
    right = (int(size * 0.72), int(size * 0.31))
    center = (size // 2, int(size * 0.42))

    draw.line(
        [left, top, right, center, left],
        fill="#f4f4ef",
        width=line_width,
        joint="curve",
    )

    lower_left = (left[0], int(size * 0.58))
    lower_center = (center[0], int(size * 0.70))
    lower_right = (right[0], int(size * 0.58))

    draw.line(
        [left, lower_left, lower_center, center],
        fill="#f4f4ef",
        width=line_width,
    )
    draw.line(
        [right, lower_right, lower_center],
        fill="#f4f4ef",
        width=line_width,
    )

    qr_x = int(size * 0.56)
    qr_y = int(size * 0.43)
    qr_size = int(size * 0.20)

    draw.rectangle(
        [
            qr_x,
            qr_y,
            qr_x + qr_size,
            qr_y + qr_size,
        ],
        fill="#f4f4ef",
    )

    cell = max(2, qr_size // 7)
    qr_pattern = [
        (1, 1), (2, 1), (4, 1), (5, 1),
        (1, 2), (5, 2),
        (1, 4), (2, 4), (4, 3), (5, 4),
        (3, 5), (5, 5),
    ]

    for col, row in qr_pattern:
        x1 = qr_x + col * cell
        y1 = qr_y + row * cell
        draw.rectangle(
            [
                x1,
                y1,
                x1 + cell,
                y1 + cell,
            ],
            fill="#111111",
        )

    badge_x = margin
    badge_y = int(size * 0.57)
    badge_w = int(size * 0.34)
    badge_h = int(size * 0.23)

    draw.rounded_rectangle(
        [
            badge_x,
            badge_y,
            badge_x + badge_w,
            badge_y + badge_h,
        ],
        radius=max(4, int(size * 0.025)),
        fill="#f4f4ef",
    )

    for i in range(3):
        y = badge_y + int(badge_h * (0.27 + i * 0.24))
        draw.line(
            [
                badge_x + int(badge_w * 0.18),
                y,
                badge_x + int(badge_w * 0.80),
                y,
            ],
            fill="#111111",
            width=max(2, int(size * 0.018)),
        )

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return HttpResponse(
        buffer.getvalue(),
        content_type="image/png",
    )


@never_cache
def service_worker(request):
    javascript = """
self.addEventListener("install", function () {
    self.skipWaiting();
});

self.addEventListener("activate", function (event) {
    event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", function (event) {
    if (event.request.method !== "GET") {
        return;
    }

    event.respondWith(
        fetch(event.request).catch(function () {
            return new Response(
                "Stone Factory ERP is offline.",
                {
                    status: 503,
                    headers: {
                        "Content-Type": "text/plain; charset=utf-8"
                    }
                }
            );
        })
    );
});
"""

    response = HttpResponse(
        javascript,
        content_type="application/javascript",
    )
    response["Service-Worker-Allowed"] = "/"

    return response
