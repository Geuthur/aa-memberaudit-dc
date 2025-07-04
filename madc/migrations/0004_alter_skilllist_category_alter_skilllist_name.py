# Generated by Django 4.2.20 on 2025-07-05 07:21

# Django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("madc", "0003_alter_skilllist_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="skilllist",
            name="category",
            field=models.CharField(
                default=None,
                help_text="Category of the skill list, used for grouping.",
                max_length=20,
                null=True,
                verbose_name="Category",
            ),
        ),
        migrations.AlterField(
            model_name="skilllist",
            name="name",
            field=models.CharField(default=None, max_length=50, null=True),
        ),
    ]
