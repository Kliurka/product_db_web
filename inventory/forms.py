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

class BaseERPForm(forms.ModelForm):
    """
    Base form for Stone Factory ERP forms.
    Applies common widget styling.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " erp-input").strip()

class ProductForm(BaseERPForm):
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


class OrderForm(BaseERPForm):
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


class CustomerForm(BaseERPForm):
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


class StorageLocationForm(BaseERPForm):
    class Meta:
        model = StorageLocation
        fields = [
            'sector',
            'number',
            'position',
            'description',
        ]


class TextureForm(BaseERPForm):
    class Meta:
        model = Texture
        fields = [
            'name',
            'image_url',
        ]


class AppUserForm(BaseERPForm):
    class Meta:
        model = AppUser
        fields = [
            'username',
            'full_name',
            'role',
            'active',
        ]