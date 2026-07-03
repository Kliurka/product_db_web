def get_sort_params(request, default_sort, allowed_sort, default_direction="asc"):
    sort = request.GET.get("sort", default_sort)
    direction = request.GET.get("dir", default_direction)

    if sort not in allowed_sort:
        sort = default_sort

    order_by = sort if direction == "asc" else "-" + sort

    return sort, direction, order_by