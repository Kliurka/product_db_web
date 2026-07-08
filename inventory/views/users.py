from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from inventory.forms import (
    AppUserCreateForm,
    AppUserEditForm,
)

from inventory.models import AppUser

# -------------------------
# Users
# -------------------------

def user_list(request):
    users = AppUser.objects.select_related("user", "role").order_by("user__username")

    return render(
        request,
        "inventory/user_list.html",
        {
            "users": users,
        },
    )


def user_add(request):
    if request.method == 'POST':
        form = AppUserCreateForm(request.POST)

        if form.is_valid():
            django_user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                is_active=form.cleaned_data['active'],
            )

            app_user = form.save(commit=False)
            app_user.user = django_user
            app_user.username = django_user.username
            app_user.password_hash = ''
            app_user.save()

            return redirect('user_edit', user_id=app_user.id)
    else:
        form = AppUserCreateForm()

    return render(request, 'inventory/user_form.html', {
        'form': form,
        'mode': 'add',
    })


def user_edit(request, user_id):
    app_user = get_object_or_404(AppUser, id=user_id)

    if request.method == 'POST':
        form = AppUserEditForm(request.POST, instance=app_user)

        if form.is_valid():
            app_user = form.save()

            app_user.user.is_active = app_user.active
            app_user.user.save()

            return redirect('user_list')
    else:
        form = AppUserEditForm(instance=app_user)

    return render(request, 'inventory/user_form.html', {
        'form': form,
        'mode': 'edit',
        'app_user': app_user,
    })
