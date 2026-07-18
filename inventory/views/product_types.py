from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from inventory.forms import ProductTypeForm
from inventory.models import ProductType
from inventory.utils.permissions import role_required


@login_required
@role_required("admin", "manager", "worker", "viewer")
def product_type_list(request):

    q = request.GET.get("q", "").strip()

    product_types = ProductType.objects.all()

    if q:
        product_types = product_types.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )

    sort = request.GET.get("sort", "name")
    direction = request.GET.get("direction", "asc")

    allowed_sort = {
        "name": "name",
    }

    sort_field = allowed_sort.get(sort, "name")

    if direction == "desc":
        product_types = product_types.order_by(f"-{sort_field}")
    else:
        product_types = product_types.order_by(sort_field)

    return render(
        request,
        "inventory/product_type_list.html",
        {
            "product_types": product_types,
            "q": q,
        },
    )
    
@login_required
@role_required("admin", "manager", "worker", "viewer")
def product_type_detail(request, pk):

    product_type = get_object_or_404(ProductType, pk=pk)

    products = product_type.products.all().order_by("code")

    return render(
        request,
        "inventory/product_type_detail.html",
        {
            "product_type": product_type,
            "products": products,
        },
    )
    
@login_required
@role_required("admin", "manager")
def product_type_add(request):

    if request.method == "POST":

        form = ProductTypeForm(request.POST)

        if form.is_valid():

            product_type = form.save(commit=False)

            product_type.created_at = timezone.now()
            product_type.updated_at = timezone.now()
            product_type.created_by = request.user.profile
            product_type.updated_by = request.user.profile

            product_type.save()

            return redirect("product_type_detail", pk=product_type.pk)

    else:

        form = ProductTypeForm()

    return render(
        request,
        "inventory/product_type_form.html",
        {
            "form": form,
            "mode": "add",
        },
    )
    
@login_required
@role_required("admin", "manager")
def product_type_edit(request, pk):

    product_type = get_object_or_404(ProductType, pk=pk)

    if request.method == "POST":

        form = ProductTypeForm(
            request.POST,
            instance=product_type,
        )

        if form.is_valid():

            product_type = form.save(commit=False)

            product_type.updated_at = timezone.now()
            product_type.updated_by = request.user.profile

            product_type.save()

            return redirect(
                "product_type_detail",
                pk=product_type.pk,
            )

    else:

        form = ProductTypeForm(instance=product_type)

    return render(
        request,
        "inventory/product_type_form.html",
        {
            "form": form,
            "product_type": product_type,
            "mode": "edit",
        },
    )