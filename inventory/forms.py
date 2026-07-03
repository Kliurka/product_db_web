from django import forms

from .models import (
    Product,
    Order,
    Discount,
    Customer,
    AppUser,
    StorageLocation,
    Texture,
)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'code',
            'name',
            'type',
            'texture',
            'dimension_x',
            'dimension_y',
            'description',
            'storage_location',
            'price',
            'status',
        ]


class OrderForm(forms.ModelForm):
    discount = forms.ModelChoiceField(
        queryset=Discount.objects.all(),
        required=False,
        label='Customer Discount',
    )

    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(status='available').order_by('code'),
        required=False,
        label='Select Product',
    )

    class Meta:
        model = Order
        fields = [
            'order_code',
            'customer',
            'payment_status',
            'partial_sum',
            'description',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['partial_sum'].required = False


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'name',
            'address',
            'phone',
            'email',
            'discount',
            'tax',
            'description',
        ]


class StorageLocationForm(forms.ModelForm):
    class Meta:
        model = StorageLocation
        fields = [
            'sector',
            'number',
            'position',
            'description',
        ]


class TextureForm(forms.ModelForm):
    class Meta:
        model = Texture
        fields = [
            'name',
            'image_url',
        ]


class AppUserForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = [
            'username',
            'full_name',
            'role',
            'active',
        ]