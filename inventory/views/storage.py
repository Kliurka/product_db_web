from django.shortcuts import get_object_or_404, redirect, render

from inventory.forms import StorageLocationForm
from inventory.models import StorageLocation, Product
from inventory.utils.sorting import get_sort_params

from django.contrib.auth.decorators import login_required
from inventory.utils.permissions import role_required
from django.utils import timezone

# -------------------------
# Storage Locations
# -------------------------

@login_required
@role_required("admin", "manager", "worker", "viewer")
def storage_list(request):
    storage_locations = StorageLocation.objects.all()

    q = request.GET.get('q', '')

    if q:
        storage_locations = storage_locations.filter(
            sector__icontains=q
        ) | StorageLocation.objects.filter(
            number__icontains=q
        ) | StorageLocation.objects.filter(
            position__icontains=q
        ) | StorageLocation.objects.filter(
            description__icontains=q
        )

    allowed_sort = [
        'sector',
        'number',
        'position',
        'description',
    ]

    sort, direction, order_by = get_sort_params(
        request,
        'sector',
        allowed_sort,
    )

    storage_locations = storage_locations.order_by(order_by)

    return render(request, 'inventory/storage_list.html', {
        'storage_locations': storage_locations,
        'q': q,
        'sort': sort,
        'direction': direction,
    })



@login_required
@role_required("admin", "manager", "worker")
def storage_add(request):
    if request.method == 'POST':
        form = StorageLocationForm(request.POST)

        if form.is_valid():
            storage = form.save(commit=False)

            storage.created_at = timezone.now()
            storage.updated_at = timezone.now()
            storage.created_by = request.user.profile
            storage.updated_by = request.user.profile

            storage.save()

            return redirect("storage_detail", pk=storage.pk)

    else:
        form = StorageLocationForm()

    return render(request, 'inventory/storage_form.html', {
        'form': form,
        'mode': 'add',
    })


@login_required
@role_required("admin", "manager", "worker")
def storage_edit(request, storage_id):
    storage = get_object_or_404(StorageLocation, id=storage_id)

    if request.method == 'POST':
        form = StorageLocationForm(request.POST, instance=storage)

        if form.is_valid():
            storage = form.save(commit=False)

            storage.updated_at = timezone.now()
            storage.updated_by = request.user.profile

            storage.save()

            return redirect("storage_detail", pk=storage.pk)
    else:
        form = StorageLocationForm(instance=storage)

    return render(request, 'inventory/storage_form.html', {
        'form': form,
        'mode': 'edit',
        'storage': storage,
    })

@login_required
@role_required("admin", "manager", "worker", "viewer")
def storage_detail(request, pk):
    storage = get_object_or_404(StorageLocation, pk=pk)

    products = storage.products.all().order_by("code")

    return render(
        request,
        "inventory/storage_detail.html",
        {
            "storage": storage,
            "products": products,
        },
    )