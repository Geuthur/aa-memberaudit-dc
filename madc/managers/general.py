"""Manager for General: app rules that Django cannot check itself.

The API, its helpers, the menu hook and the access querysets check permissions
only through this manager (``General.objects``). The Django views keep
``@permission_required("madc.<permission>")``.
General is unmanaged, so this manager never queries the database.
"""

# Django
from django.db import models

# Alliance Auth
from allianceauth.authentication.models import User


class GeneralManager(models.Manager):
    def has_basic_access(self, user: User) -> bool:
        """True if the user may use the app (basic_access)."""
        return bool(user.has_perm("madc.basic_access"))

    def has_corp_access(self, user: User) -> bool:
        """True if the user may see characters of their own corporation."""
        return bool(user.has_perm("madc.corp_access"))

    def has_alliance_access(self, user: User) -> bool:
        """True if the user may see characters of their own alliance."""
        return bool(user.has_perm("madc.alliance_access"))

    def has_management_access(self, user: User) -> bool:
        """True if the user may manage (manage_access or admin_access)."""
        return bool(
            user.has_perm("madc.manage_access") or user.has_perm("madc.admin_access")
        )

    def has_admin_access(self, user: User) -> bool:
        """True if the user has admin_access."""
        return bool(user.has_perm("madc.admin_access"))

    def has_full_access(self, user: User) -> bool:
        """True for superusers and users with admin_access: they see everything."""
        return bool(user.is_superuser) or self.has_admin_access(user)
