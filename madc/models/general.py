# Standard Library

# Django
from django.contrib.auth.models import Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth (External Libs)
from app_utils.django import users_with_permission

# AA Memberaudit Doctrine Checker
from madc.managers.general_manager import GeneralManager


class General(models.Model):
    """A model defining commonly used properties and methods for Memberaudit Doctrine Checker."""

    objects = GeneralManager()

    class Meta:
        managed = False
        default_permissions = ()
        verbose_name = "AA-Memberaudit-Doctrine-Checker"
        verbose_name_plural = "AA-Memberaudit-Doctrine-Checker"
        permissions = (
            ("basic_access", _("Can access this app, Memberaudit Doctrine Checker.")),
            (
                "corp_access",
                _(
                    "Can view Characters from own Corporation, Memberaudit Doctrine Checker."
                ),
            ),
            (
                "alliance_access",
                _(
                    "Can view Characters from own Alliance, Memberaudit Doctrine Checker."
                ),
            ),
            ("manage_access", _("Can manage this app, Memberaudit Doctrine Checker.")),
            (
                "admin_access",
                _("Gives full access to this app, Memberaudit Doctrine Checker."),
            ),
        )

    @classmethod
    def basic_permission(cls):
        """Return basic permission needed to use this app."""
        return Permission.objects.select_related("content_type").get(
            content_type__app_label=cls._meta.app_label, codename="basic_access"
        )

    @classmethod
    def users_with_basic_access(cls) -> models.QuerySet:
        """Return users which have at least basic access to Memberaudit Doctrine Checker."""
        return users_with_permission(cls.basic_permission())
