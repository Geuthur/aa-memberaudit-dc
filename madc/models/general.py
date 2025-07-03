# Standard Library

# Django
from django.contrib.auth.models import Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.django import users_with_permission
from app_utils.logging import LoggerAddTag

# AA Memberaudit Doctrine Checker
from madc import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


class General(models.Model):
    """A model defining commonly used properties and methods for Voices of War."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app, Voices of War."),
            ("manage_access", "Has access to moderation tools"),
            ("admin_access", "Has access to all Administration tools"),
        )

    @classmethod
    def basic_permission(cls):
        """Return basic permission needed to use this app."""
        return Permission.objects.select_related("content_type").get(
            content_type__app_label=cls._meta.app_label, codename="basic_access"
        )

    @classmethod
    def users_with_basic_access(cls) -> models.QuerySet:
        """Return users which have at least basic access to Voices of War."""
        return users_with_permission(cls.basic_permission())
