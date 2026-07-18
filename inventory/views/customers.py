from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from inventory.forms import CustomerForm
from inventory.models import (
    Customer,
    Discount,
    Tax,
)
from inventory.utils.sorting import get_sort_params
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from inventory.utils.permissions import role_required

@login_required

def customer_list(request):
    customers = Customer.objects.annotate(
        orders_count=Count('order')
    )

    q = request.GET.get('q', '')
    selected_discount = request.GET.get('discount', '')
    selected_tax = request.GET.get('tax', '')
    has_orders = request.GET.get('has_orders', '')


    if q:
        customers = customers.filter(name__icontains=q)

    if selected_discount:
        customers = customers.filter(discount_id=selected_discount)

    if selected_tax:
        customers = customers.filter(tax_id=selected_tax)

    if has_orders == 'yes':
        customers = customers.filter(orders_count__gt=0)

    if has_orders == 'no':
        customers = customers.filter(orders_count=0)

    allowed_sort = [
        'name',
        'phone',
        'email',
        'discount__percent',
        'tax__percent',
        'orders_count',
    ]

    sort, direction, order_by = get_sort_params(
        request,
        'name',
        allowed_sort,
    )
    customers = customers.order_by(order_by)

    return render(request, 'inventory/customer_list.html', {
        'customers': customers,
        'q': q,
        'discounts': Discount.objects.all(),
        'taxes': Tax.objects.all(),
        'selected_discount': selected_discount,
        'selected_tax': selected_tax,
        'has_orders': has_orders,
        'sort': sort,
        'direction': direction,
    })

@login_required
@role_required("admin", "manager")

def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save(commit=False)

            customer.created_at = timezone.now()
            customer.updated_at = timezone.now()
            customer.created_by = request.user.profile
            customer.updated_by = request.user.profile

            customer.save()

            return redirect("customer_detail", pk=customer.pk)
    else:
        form = CustomerForm()

    return render(request, 'inventory/customer_form.html', {
        'form': form,
        'mode': 'add',
    })


@login_required
@role_required("admin", "manager")

def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)

        if form.is_valid():
            customer = form.save(commit=False)

            customer.updated_at = timezone.now()
            customer.updated_by = request.user.profile

            customer.save()

            return redirect("customer_detail", pk=customer.pk)
        
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'inventory/customer_form.html', {
        'form': form,
        'mode': 'edit',
        'customer': customer,
    })


@login_required
@role_required("admin", "manager")
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    return render(
        request,
        "inventory/customer_detail.html",
        {
            "customer": customer,
        },
    )