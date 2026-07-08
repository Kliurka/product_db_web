from django.shortcuts import render

from inventory.models import Customer, Order, Product


def dashboard(request):
    products_count = Product.objects.count()
    available_products_count = Product.objects.filter(status='available').count()
    reserved_products_count = Product.objects.filter(status='reserved').count()
    orders_count = Order.objects.count()
    customers_count = Customer.objects.count()

    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:5]

    return render(request, 'inventory/dashboard.html', {
        'products_count': products_count,
        'available_products_count': available_products_count,
        'reserved_products_count': reserved_products_count,
        'orders_count': orders_count,
        'customers_count': customers_count,
        'recent_orders': recent_orders,
    })