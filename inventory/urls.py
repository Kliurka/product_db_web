from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('scan/', views.scan_qr, name='scan_qr'),
    
    path('orders/', views.order_list, name='order_list'),
    path('orders/add/', views.order_add, name='order_add'),
    path('order/<str:order_code>/', views.order_detail, name='order_detail'),
    path('order/<str:order_code>/edit/', views.order_edit, name='order_edit'),

    path('products/add/', views.product_add, name='product_add'), 
    path('product/<str:code>/edit/', views.product_edit, name='product_edit'),
    path('product/<str:code>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/qr/', views.product_qr, name='product_qr'),
    path('product/<str:code>/photos/add/', views.product_image_add, name='product_image_add'),
    path("product/photo/<int:image_id>/delete/", views.product_image_delete, name="product_image_delete",),
    
    path("product-types/", views.product_type_list, name="product_type_list"),
    path("product-types/add/", views.product_type_add, name="product_type_add"),
    path("product-types/<int:pk>/", views.product_type_detail, name="product_type_detail"),
    path("product-types/<int:pk>/edit/", views.product_type_edit, name="product_type_edit"),
    
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/add/", views.customer_add, name="customer_add"),
    path("customers/<int:pk>/", views.customer_detail, name="customer_detail"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    
    path('storage/', views.storage_list, name='storage_list'),
    path('storage/add/', views.storage_add, name='storage_add'),
    path('storage/<int:storage_id>/edit/', views.storage_edit, name='storage_edit'),
    path("storage/<int:pk>/", views.storage_detail, name="storage_detail"),
        
    path("textures/", views.texture_list, name="texture_list"),
    path("textures/add/", views.texture_add, name="texture_add"),
    path("textures/<int:pk>/", views.texture_detail, name="texture_detail"),
    path("textures/<int:pk>/edit/", views.texture_edit, name="texture_edit"),

    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    
    path("discounts/", views.discount_list, name="discount_list"),
    path("discounts/add/", views.discount_add, name="discount_add"),
    path("discounts/<int:pk>/", views.discount_detail, name="discount_detail"),
    path("discounts/<int:pk>/edit/", views.discount_edit, name="discount_edit"),
    
    path("taxes/", views.tax_list, name="tax_list"),
    path("taxes/add/", views.tax_add, name="tax_add"),
    path("taxes/<int:pk>/", views.tax_detail, name="tax_detail"),
    path("taxes/<int:pk>/edit/", views.tax_edit, name="tax_edit"),
]
