from django.shortcuts import get_object_or_404, redirect, render

from inventory.forms import ProductImageForm
from inventory.models import Product, ProductImage
from django.contrib import messages
import os

def product_image_add(request, code):
    product = get_object_or_404(Product, code=code)

    if request.method == 'POST':
        form = ProductImageForm(
            request.POST,
            request.FILES,
            initial={'product': product},
        )

        if form.is_valid():
            product_image = form.save(commit=False)
            product_image.product = product
            product_image.save()

            return redirect('product_edit', code=product.code)
    else:
        form = ProductImageForm(initial={'product': product})

    return render(request, 'inventory/product_image_form.html', {
        'form': form,
        'product': product,
    })


def product_image_delete(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)

    product_code = image.product.code

    if image.image:
        image.image.delete(save=False)

    image.delete()

    messages.success(request, "Photo deleted.")

    return redirect("product_edit", code=product_code)