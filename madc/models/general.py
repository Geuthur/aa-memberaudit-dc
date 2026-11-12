"""Models for General."""

# Standard Library
from typing import Any

# Django
from django.contrib.auth.models import Permission as AuthPermission
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth (External Libs)
from app_utils.django import users_with_permission


class General(models.Model):
    """A model defining commonly used properties, permissions, and helper methods for Memberaudit Doctrine Checker."""

    class Permission(models.TextChoices):
        BASIC_ACCESS = "basic_access", _(
            "Can access this app, Memberaudit Doctrine Checker."
        )
        CORP_ACCESS = "corp_access", _(
            "Can view Characters from own Corporation, Memberaudit Doctrine Checker."
        )
        ALLIANCE_ACCESS = "alliance_access", _(
            "Can view Characters from own Alliance, Memberaudit Doctrine Checker."
        )
        MANAGE_ACCESS = "manage_access", _(
            "Can manage this app, Memberaudit Doctrine Checker."
        )
        ADMIN_ACCESS = "admin_access", _(
            "Gives full access to this app, Memberaudit Doctrine Checker."
        )

    class Meta:
        managed = False
        default_permissions = ()  # Remove standard permissions
        verbose_name = "AA-Memberaudit-Doctrine-Checker"
        verbose_name_plural = "AA-Memberaudit-Doctrine-Checker"

    # Inject dynamic permissions
    Meta.permissions = Permission.choices

    @classmethod
    def get_perm(cls, perm: "str | Permission") -> str:
        """Return full permission string 'madc.<codename>'."""
        codename = perm.value if isinstance(perm, cls.Permission) else perm
        return f"madc.{codename}"

    @classmethod
    def has_perm(cls, user: Any, perm: "str | General.Permission") -> bool:
        """Check if user has permission."""
        if not user or not hasattr(user, "has_perm"):
            return False
        return user.has_perm(cls.get_perm(perm))

    @classmethod
    def has_any_perm(cls, user: Any, *perms: "str | General.Permission") -> bool:
        """Return True if user has any of the specified permissions."""
        if not user or not hasattr(user, "has_perm"):
            return False
        return any(user.has_perm(cls.get_perm(p)) for p in perms)

    @classmethod
    def has_management_access(cls, user: Any) -> bool:
        """Check if user has any management permission."""
        return cls.has_any_perm(
            user,
            cls.Permission.MANAGE_ACCESS,
            cls.Permission.ADMIN_ACCESS,
        )

    @classmethod
    def basic_permission(cls):
        """Return basic permission needed to use this app."""
        return AuthPermission.objects.select_related("content_type").get(
            content_type__app_label=cls._meta.app_label,
            codename=cls.Permission.BASIC_ACCESS.value,  # pylint: disable=no-member
        )

    @classmethod
    def users_with_basic_access(cls) -> models.QuerySet:
        """Return users which have at least basic access to Memberaudit Doctrine Checker."""
        return users_with_permission(cls.basic_permission())
