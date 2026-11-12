"""Manager for General: app rules that Django cannot check itself.

General is unmanaged, so this manager never queries the database.
"""

# Django
from django.db import models

# Alliance Auth
from allianceauth.authentication.models import User


class GeneralManager(models.Manager):
    def has_management_access(self, user: User) -> bool:
        """True if the user may manage (manage_access or admin_access)."""
        return bool(
            user.has_perm("madc.manage_access") or user.has_perm("madc.admin_access")
        )
