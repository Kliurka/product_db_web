from django.db import migrations


def migrate_users(apps, schema_editor):
    AppUser = apps.get_model("inventory", "AppUser")
    User = apps.get_model("auth", "User")

    for app_user in AppUser.objects.all():

        django_user, created = User.objects.get_or_create(
            username=app_user.username,
            defaults={
                "is_active": app_user.active,
            },
        )

        app_user.user = django_user
        app_user.save(update_fields=["user"])


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0007_appuser_user"),   # <- paskutinė tavo migracija
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(migrate_users),
    ]