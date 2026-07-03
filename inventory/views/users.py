from django.shortcuts import get_object_or_404, redirect, render

from inventory.forms import AppUserForm
from inventory.models import (
    AppUser,
    Role,
)
from inventory.utils.sorting import get_sort_params


# -------------------------
# Users
# -------------------------

def user_list(request):
    users = AppUser.objects.select_related('role')

    q = request.GET.get('q', '')
    selected_role = request.GET.get('role', '')
    active = request.GET.get('active', '')


    if q:
        users = users.filter(
            username__icontains=q
        ) | AppUser.objects.select_related('role').filter(
            full_name__icontains=q
        )

    if selected_role:
        users = users.filter(role_id=selected_role)

    if active == 'yes':
        users = users.filter(active=True)

    if active == 'no':
        users = users.filter(active=False)

    allowed_sort = [
        'username',
        'full_name',
        'role__name',
        'active',
        'last_login',
    ]
    sort, direction, order_by = get_sort_params(
        request,
        'username',
        allowed_sort,
    )

    users = users.order_by(order_by)


    return render(request, 'inventory/user_list.html', {
        'users': users,
        'roles': Role.objects.all(),
        'q': q,
        'selected_role': selected_role,
        'active': active,
        'sort': sort,
        'direction': direction,
    })


def user_add(request):
    if request.method == 'POST':
        form = AppUserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.password_hash = ''
            user.save()
            return redirect('user_edit', user_id=user.id)
    else:
        form = AppUserForm()

    return render(request, 'inventory/user_form.html', {
        'form': form,
        'mode': 'add',
    })


def user_edit(request, user_id):
    app_user = get_object_or_404(AppUser, id=user_id)

    if request.method == 'POST':
        form = AppUserForm(request.POST, instance=app_user)

        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = AppUserForm(instance=app_user)

    return render(request, 'inventory/user_form.html', {
        'form': form,
        'mode': 'edit',
        'app_user': app_user,
    })

