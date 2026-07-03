from django.shortcuts import get_object_or_404, redirect, render

from inventory.forms import TextureForm
from inventory.models import Texture
from inventory.utils.sorting import get_sort_params


# -------------------------
# Textures
# -------------------------

def texture_list(request):
    textures = Texture.objects.all()

    q = request.GET.get('q', '')

    if q:
        textures = textures.filter(name__icontains=q)

    allowed_sort = [
        'name',
    ]

    sort, direction, order_by = get_sort_params(
        request,
        'name',
        allowed_sort,
    )

    textures = textures.order_by(order_by)

    return render(request, 'inventory/texture_list.html', {
        'textures': textures,
        'q': q,
        'sort': sort,
        'direction': direction,
    })

def texture_add(request):
    if request.method == 'POST':
        form = TextureForm(request.POST)

        if form.is_valid():
            texture = form.save()
            return redirect('texture_edit', texture_id=texture.id)
    else:
        form = TextureForm()

    return render(request, 'inventory/texture_form.html', {
        'form': form,
        'mode': 'add',
    })


def texture_edit(request, texture_id):
    texture = get_object_or_404(Texture, id=texture_id)

    if request.method == 'POST':
        form = TextureForm(request.POST, instance=texture)

        if form.is_valid():
            form.save()
            return redirect('texture_list')
    else:
        form = TextureForm(instance=texture)

    return render(request, 'inventory/texture_form.html', {
        'form': form,
        'mode': 'edit',
        'texture': texture,
    })
