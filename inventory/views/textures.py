from django.shortcuts import get_object_or_404, redirect, render

from inventory.forms import TextureForm
from inventory.models import Texture
from inventory.utils.sorting import get_sort_params

from django.contrib.auth.decorators import login_required
from inventory.utils.permissions import role_required
from django.utils import timezone
from django.db.models import Q

# -------------------------
# Textures
# -------------------------
@login_required
@role_required("admin", "manager", "worker", "viewer")
def texture_list(request):

    q = request.GET.get("q", "").strip()

    textures = Texture.objects.all()

    if q:
        textures = textures.filter(
            Q(name__icontains=q)
        )

    sort = request.GET.get("sort", "name")
    direction = request.GET.get("direction", "asc")

    allowed_sort = {
        "name": "name",
    }

    sort_field = allowed_sort.get(sort, "name")

    if direction == "desc":
        textures = textures.order_by(f"-{sort_field}")
    else:
        textures = textures.order_by(sort_field)

    return render(
        request,
        "inventory/texture_list.html",
        {
            "textures": textures,
            "q": q,
        },
    )

@login_required
@role_required("admin", "manager")
def texture_add(request):
    if request.method == "POST":
        form = TextureForm(request.POST, request.FILES)

        if form.is_valid():
            texture = form.save(commit=False)

            texture.created_at = timezone.now()
            texture.updated_at = timezone.now()
            texture.created_by = request.user.profile
            texture.updated_by = request.user.profile

            texture.save()

            return redirect("texture_detail", pk=texture.pk)
    else:
        form = TextureForm()

    return render(
        request,
        "inventory/texture_form.html",
        {
            "form": form,
            "page_title": "Add Texture",
        },
    )

@login_required
@role_required("admin", "manager")
def texture_edit(request, pk):
    texture = get_object_or_404(Texture, pk=pk)

    if request.method == "POST":
        form = TextureForm(
            request.POST,
            request.FILES,
            instance=texture,
        )

        if form.is_valid():
            texture = form.save(commit=False)

            texture.updated_at = timezone.now()
            texture.updated_by = request.user.profile

            texture.save()

            return redirect("texture_detail", pk=texture.pk)
    else:
        form = TextureForm(instance=texture)

    return render(
        request,
        "inventory/texture_form.html",
        {
            "form": form,
            "texture": texture,
            "page_title": "Edit Texture",
        },
    )

@login_required
@role_required("admin", "manager", "worker", "viewer")
def texture_detail(request, pk):
    texture = get_object_or_404(Texture, pk=pk)

    products = texture.product_set.all().order_by("code")

    return render(
        request,
        "inventory/texture_detail.html",
        {
            "texture": texture,
            "products": products,
        },
    )