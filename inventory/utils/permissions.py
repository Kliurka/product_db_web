from functools import wraps

from django.http import HttpResponseForbidden


def get_user_role(user):
    if not user.is_authenticated:
        return None

    profile = getattr(user, "profile", None)

    if profile is None or profile.role is None:
        return None

    return profile.role.name.lower()


def role_required(*allowed_roles):
    allowed_roles = [role.lower() for role in allowed_roles]

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            role = get_user_role(request.user)

            if role in allowed_roles:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("Permission denied.")

        return wrapper

    return decorator
