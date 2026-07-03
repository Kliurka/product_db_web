from django.shortcuts import get_object_or_404, redirect, render

from inventory.forms import StorageLocationForm
from inventory.models import StorageLocation
from inventory.utils.sorting import get_sort_params


# -------------------------
# Storage Locations
# -------------------------

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

def storage_add(request):
    if request.method == 'POST':
        form = StorageLocationForm(request.POST)

        if form.is_valid():
            storage = form.save()
            return redirect('storage_edit', storage_id=storage.id)
    else:
        form = StorageLocationForm()

    return render(request, 'inventory/storage_form.html', {
        'form': form,
        'mode': 'add',
    })


def storage_edit(request, storage_id):
    storage = get_object_or_404(StorageLocation, id=storage_id)

    if request.method == 'POST':
        form = StorageLocationForm(request.POST, instance=storage)

        if form.is_valid():
            form.save()
            return redirect('storage_list')
    else:
        form = StorageLocationForm(instance=storage)

    return render(request, 'inventory/storage_form.html', {
        'form': form,
        'mode': 'edit',
        'storage': storage,
    })
