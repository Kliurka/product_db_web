from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('products/', views.product_list, name='product_list'),
    path('scan/', views.scan_qr, name='scan_qr'),
    
    path('orders/', views.order_list, name='order_list'),
    path('orders/add/', views.order_add, name='order_add'),
    path('orders/<str:order_code>/edit/', views.order_edit, name='order_edit'),

    path('products/add/', views.product_add, name='product_add'), 
    path('product/<str:code>/edit/', views.product_edit, name='product_edit'),
    path('product/<str:code>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/qr/', views.product_qr, name='product_qr'),
]
