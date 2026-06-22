from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Role, AppUser, Discount, Tax, Customer,
    ProductType, Texture, StorageLocation,
    Product, ProductImage, Order, Payment, Reservation
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'texture',
        'storage_location',
        'price',
        'status',
        'qr_link',
    )

    search_fields = (
        'code',
        'name'
    )

    list_filter = (
        'status',
        'texture',
        'type'
    )

    def qr_link(self, obj):
        url = reverse('product_qr', args=[obj.id])
        return format_html('<a href="{}" target="_blank">QR</a>', url)

    qr_link.short_description = 'QR'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'phone',
        'email'
    )

    search_fields = (
        'name',
        'phone',
        'email'
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_code',
        'customer',
        'payment_status',
        'partial_sum'
    )

    search_fields = (
        'order_code',
        'customer__name'
    )

    list_filter = (
        'payment_status',
    )


admin.site.register(Role)
admin.site.register(AppUser)
admin.site.register(Discount)
admin.site.register(Tax)
admin.site.register(ProductType)
admin.site.register(Texture)
admin.site.register(StorageLocation)
admin.site.register(ProductImage)
admin.site.register(Payment)
admin.site.register(Reservation)
