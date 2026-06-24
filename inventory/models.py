from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.name


class AppUser(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.TextField()
    full_name = models.CharField(max_length=100, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, blank=True, null=True, db_column='role_id')
    active = models.BooleanField(default=True)
    last_login = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username


class Discount(models.Model):
    name = models.CharField(max_length=100)
    percent = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'discounts'

    def __str__(self):
        return self.name


class Tax(models.Model):
    name = models.CharField(max_length=100)
    percent = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'taxes'

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, blank=True, null=True, db_column='discount_id')
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, blank=True, null=True, db_column='tax_id')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(AppUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_customers', db_column='created_by')
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey(AppUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='updated_customers', db_column='updated_by')

    class Meta:
        db_table = 'customers'

    def __str__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'types'

    def __str__(self):
        return self.name


class Texture(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image_url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'textures'

    def __str__(self):
        return self.name


class StorageLocation(models.Model):
    sector = models.CharField(max_length=50, blank=True, null=True)
    number = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'storage_locations'

    def __str__(self):
        return f"{self.sector}-{self.number}-{self.position}"


class Product(models.Model):
    PRODUCT_STATUS = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
        ('shipped', 'Shipped'),
        ('returned', 'Returned'),
        ('damaged', 'Damaged'),
        ('archived', 'Archived'),
    ]

    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, blank=True, null=True, db_column='type_id')
    description = models.TextField(blank=True, null=True)
    storage_location = models.ForeignKey(StorageLocation, on_delete=models.SET_NULL, blank=True, null=True, db_column='storage_location_id')
    dimension_x = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dimension_y = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    texture = models.ForeignKey(Texture, on_delete=models.SET_NULL, blank=True, null=True, db_column='texture_id')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=50, choices=PRODUCT_STATUS, default='available')
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(AppUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_products', db_column='created_by')
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey(AppUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='updated_products', db_column='updated_by')

    def qr_text(self):
        return self.code

    class Meta:
        db_table = 'products'

    def __str__(self):
        return f"{self.code} - {self.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image_url = models.TextField()
    image_type = models.CharField(max_length=50, default='gallery')
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'product_images'

    def __str__(self):
        return self.image_url


class Order(models.Model):
    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    order_code = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id')
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS, default='unpaid')
    partial_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(AppUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_orders', db_column='created_by')
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey(AppUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='updated_orders', db_column='updated_by')
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return self.order_code

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_column='order_id'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='product_id'
    )

    product_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    product_name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    tax_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=21
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f"{self.product_code} ({self.order.order_code})"

class Payment(models.Model):
    PAYMENT_TYPE = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank transfer'),
        ('card', 'Card'),
        ('other', 'Other'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE, default='cash')
    paid_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(AppUser, on_delete=models.SET_NULL, blank=True, null=True, db_column='created_by')
    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'payments'

    def __str__(self):
        return f"{self.order} - {self.amount}"


class Reservation(models.Model):
    RESERVATION_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    reserved_at = models.DateTimeField(blank=True, null=True)
    reserved_by = models.ForeignKey(AppUser, on_delete=models.SET_NULL, blank=True, null=True, db_column='reserved_by')
    status = models.CharField(max_length=50, choices=RESERVATION_STATUS, default='active')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'reservations'

    def __str__(self):
        return f"{self.product} -> {self.order}"
