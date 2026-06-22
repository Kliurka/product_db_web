from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def sort_link(context, field, label):
    request = context["request"]

    current_sort = request.GET.get("sort", "")
    current_dir = request.GET.get("dir", "asc")

    params = request.GET.copy()
    params["sort"] = field

    if current_sort == field and current_dir == "asc":
        params["dir"] = "desc"
        arrow = "▲"
    elif current_sort == field and current_dir == "desc":
        params["dir"] = "asc"
        arrow = "▼"
    else:
        params["dir"] = "asc"
        arrow = ""

    url = "?" + params.urlencode()

    if arrow:
        html = f'<a class="sort-link active" href="{url}">{label} <span>{arrow}</span></a>'
    else:
        html = f'<a class="sort-link" href="{url}">{label}</a>'

    return mark_safe(html)