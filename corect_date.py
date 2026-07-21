import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "productdb.settings")
django.setup()

from django.utils import timezone
from inventory.models import Order

tz = timezone.get_current_timezone()

fixed = 0

for order in Order.objects.all():
    fields = []

    if order.created_at and timezone.is_naive(order.created_at):
        order.created_at = timezone.make_aware(order.created_at, tz)
        fields.append("created_at")

    if order.updated_at and timezone.is_naive(order.updated_at):
        order.updated_at = timezone.make_aware(order.updated_at, tz)
        fields.append("updated_at")

    if fields:
        order.save(update_fields=fields)
        fixed += 1

print(f"Pataisyta {fixed} užsakymų.")