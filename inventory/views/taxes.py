from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from inventory.forms import TaxForm
from inventory.models import Tax
from inventory.utils.permissions import role_required


@login_required
@role_required("admin", "manager")
def tax_list(request):

    q = request.GET.get("q", "").strip()

    taxes = Tax.objects.all()

    if q:
        taxes = taxes.filter(
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
        taxes = taxes.order_by(f"-{sort_field}")
    else:
        taxes = taxes.order_by(sort_field)

    return render(
        request,
        "inventory/tax_list.html",
        {
            "taxes": taxes,
            "q": q,
        },
    )
    
    
@login_required
@role_required("admin", "manager")
def tax_detail(request, pk):

    tax = get_object_or_404(
        Tax,
        pk=pk,
    )

    return render(
        request,
        "inventory/tax_detail.html",
        {
            "tax": tax,
        },
    )

@login_required
@role_required("admin", "manager")
def tax_add(request):

    if request.method == "POST":

        form = TaxForm(request.POST)

        if form.is_valid():

            tax = form.save(commit=False)

            tax.created_at = timezone.now()
            tax.updated_at = timezone.now()
            tax.created_by = request.user.profile
            tax.updated_by = request.user.profile

            tax.save()

            return redirect(
                "tax_detail",
                pk=tax.pk,
            )

    else:

        form = TaxForm()

    return render(
        request,
        "inventory/tax_form.html",
        {
            "form": form,
            "mode": "add",
        },
    )    
    
    
@login_required
@role_required("admin", "manager")
def tax_edit(request, pk):

    tax = get_object_or_404(
        Tax,
        pk=pk,
    )

    if request.method == "POST":

        form = TaxForm(
            request.POST,
            instance=tax,
        )

        if form.is_valid():

            tax = form.save(commit=False)

            tax.updated_at = timezone.now()
            tax.updated_by = request.user.profile

            tax.save()

            return redirect(
                "tax_detail",
                pk=tax.pk,
            )

    else:

        form = TaxForm(instance=tax)

    return render(
        request,
        "inventory/tax_form.html",
        {
            "form": form,
            "tax": tax,
            "mode": "edit",
        },
    )