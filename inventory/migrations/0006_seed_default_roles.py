from django.db import migrations


def seed_roles(apps, schema_editor):
    Role = apps.get_model("inventory", "Role")

    roles = [
        "admin",
        "manager",
        "worker",
        "viewer",
    ]

    for role_name in roles:
        Role.objects.get_or_create(name=role_name)


def remove_roles(apps, schema_editor):
    Role = apps.get_model("inventory", "Role")

    Role.objects.filter(
        name__in=[
            "admin",
            "manager",
            "worker",
            "viewer",
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0005_alter_productimage_image"),
    ]

    operations = [
        migrations.RunPython(seed_roles, remove_roles),
    ]