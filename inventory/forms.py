from django import forms

from .models import (
    Product,
    ProductImage,
    Order,
    Discount,
    Customer,
    AppUser,
    StorageLocation,
    Texture,
)

from inventory.utils.images import process_uploaded_image
from django.contrib.auth.models import User



CAMERA_FILE_INPUT = forms.FileInput(attrs={
    "accept": "image/*",
    "capture": "environment",
})

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

class ProductImageForm(BaseERPForm):
    class Meta:
        model = ProductImage
        fields = ['image']

        widgets = {
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
                'capture': 'environment',
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if not image:
            return image

        product = self.initial.get('product')

        prefix = product.code if product else 'product'

        return process_uploaded_image(
            image,
            size=(1600, 1600),
            filename_prefix=prefix,
        )

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
            'image',
        ]

        widgets = {
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
                'capture': 'environment',
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if not image:
            return image

        return process_uploaded_image(
            image,
            size=(800, 800),
            filename_prefix=self.cleaned_data.get('name') or 'texture',
        )


class AppUserCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = AppUser
        fields = [
            'full_name',
            'role',
            'active',
        ]

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")

        return username

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data


class AppUserEditForm(BaseERPForm):
    class Meta:
        model = AppUser
        fields = [
            'full_name',
            'role',
            'active',
        ]