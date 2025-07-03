"""App Configuration"""

# Django
from django.apps import AppConfig

# AA Memberaudit Doctrine Checker
from madc import __version__


class DoctrineCheckerConfig(AppConfig):
    """App Config"""

    default_auto_field = "django.db.models.AutoField"
    name = "madc"
    label = "madc"
    verbose_name = f"AA Memberaudit Doctrine Checker v{__version__}"
