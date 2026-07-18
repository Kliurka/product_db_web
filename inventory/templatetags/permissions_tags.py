from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def user_role(context):
    user = context["request"].user

    if not user.is_authenticated:
        return ""

    profile = getattr(user, "profile", None)

    if profile is None or profile.role is None:
        return ""

    return profile.role.name.lower()


@register.filter
def has_role(user, role):

    if not user.is_authenticated:
        return False

    profile = getattr(user, "profile", None)

    if profile is None or profile.role is None:
        return False

    return profile.role.name.lower() == role.lower()
