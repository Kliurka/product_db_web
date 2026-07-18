from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from inventory.forms import DiscountForm
from inventory.models import Discount
from inventory.utils.permissions import role_required


@login_required
@role_required("admin", "manager")
def discount_list(request):

    q = request.GET.get("q", "").strip()

    discounts = Discount.objects.all()

    if q:
        discounts = discounts.filter(
            Q(name__icontains=q)
        )

    sort = request.GET.get("sort", "percent")
    direction = request.GET.get("direction", "asc")

    allowed_sort = {
        "name": "name",
        "percent": "percent",
    }

    sort_field = allowed_sort.get(sort, "percent")

    if direction == "desc":
        discounts = discounts.order_by(f"-{sort_field}")
    else:
        discounts = discounts.order_by(sort_field)

    return render(
        request,
        "inventory/discount_list.html",
        {
            "discounts": discounts,
            "q": q,
        },
    )
    
    
@login_required
@role_required("admin", "manager")
def discount_detail(request, pk):

    discount = get_object_or_404(
        Discount,
        pk=pk,
    )

    return render(
        request,
        "inventory/discount_detail.html",
        {
            "discount": discount,
        },
    )

@login_required
@role_required("admin", "manager")
def discount_add(request):

    if request.method == "POST":

        form = DiscountForm(request.POST)

        if form.is_valid():

            discount = form.save(commit=False)

            discount.created_at = timezone.now()
            discount.updated_at = timezone.now()
            discount.created_by = request.user.profile
            discount.updated_by = request.user.profile

            discount.save()

            return redirect(
                "discount_detail",
                pk=discount.pk,
            )

    else:

        form = DiscountForm()

    return render(
        request,
        "inventory/discount_form.html",
        {
            "form": form,
            "mode": "add",
        },
    )    
    
    
@login_required
@role_required("admin", "manager")
def discount_edit(request, pk):

    discount = get_object_or_404(
        Discount,
        pk=pk,
    )

    if request.method == "POST":

        form = DiscountForm(
            request.POST,
            instance=discount,
        )

        if form.is_valid():

            discount = form.save(commit=False)

            discount.updated_at = timezone.now()
            discount.updated_by = request.user.profile

            discount.save()

            return redirect(
                "discount_detail",
                pk=discount.pk,
            )

    else:

        form = DiscountForm(instance=discount)

    return render(
        request,
        "inventory/discount_form.html",
        {
            "form": form,
            "discount": discount,
            "mode": "edit",
        },
    )