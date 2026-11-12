# Django
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("madc", "0004_alter_skilllist_category_alter_skilllist_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="general",
            options={
                "default_permissions": (),
                "managed": False,
                "permissions": [
                    (
                        "basic_access",
                        "Can access this app, Memberaudit Doctrine Checker.",
                    ),
                    (
                        "corp_access",
                        "Can view Characters from own Corporation, Memberaudit Doctrine Checker.",
                    ),
                    (
                        "alliance_access",
                        "Can view Characters from own Alliance, Memberaudit Doctrine Checker.",
                    ),
                    (
                        "manage_access",
                        "Can manage this app, Memberaudit Doctrine Checker.",
                    ),
                    (
                        "admin_access",
                        "Gives full access to this app, Memberaudit Doctrine Checker.",
                    ),
                ],
                "verbose_name": "AA-Memberaudit-Doctrine-Checker",
                "verbose_name_plural": "AA-Memberaudit-Doctrine-Checker",
            },
        ),
    ]
