"""Check that all permission strings used in the code are defined in General."""

# Standard Library
import re
from pathlib import Path

# Django
from django.test import SimpleTestCase

# AA Memberaudit Doctrine Checker
import madc
from madc.models import SkillList
from madc.models.general import General
from madc.tests import AuthTestCase
from madc.tests.testdata.app import UserMainFactory

# Matches e.g. "madc.basic_access" and "perms.madc.basic_access", also typos
PERMISSION_PATTERN = re.compile(r"\bmadc\.(\w*access\w*)", re.IGNORECASE)


class TestPermissionStrings(SimpleTestCase):
    def test_used_permissions_exist_in_general(self):
        """Every permission string in the code must match a codename of General."""
        defined = {codename for codename, _ in General._meta.permissions}
        root = Path(madc.__file__).parent
        used = {}
        for path in root.rglob("*"):
            if path.suffix not in {".py", ".html"} or "tests" in path.parts:
                continue
            if "migrations" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for match in PERMISSION_PATTERN.finditer(text):
                used.setdefault(match.group(1), set()).add(path.name)

        self.assertTrue(used, "No permission strings found, pattern is broken.")
        unknown = {k: sorted(v) for k, v in used.items() if k not in defined}
        self.assertEqual(unknown, {})

    def test_all_defined_permissions_are_used(self):
        """Every permission defined in General must be checked somewhere."""
        defined = {codename for codename, _ in General._meta.permissions}
        root = Path(madc.__file__).parent
        used = set()
        for path in root.rglob("*"):
            if path.suffix not in {".py", ".html"} or "tests" in path.parts:
                continue
            if "migrations" in path.parts:
                continue
            used |= set(PERMISSION_PATTERN.findall(path.read_text(encoding="utf-8")))
        self.assertEqual(defined - used, set())


class TestGeneralManager(AuthTestCase):
    def test_has_management_access(self):
        for perm, expected in (
            ("madc.manage_access", True),
            ("madc.admin_access", True),
            ("madc.basic_access", False),
        ):
            user = UserMainFactory(permissions__=[perm])
            self.assertEqual(General.objects.has_management_access(user), expected)

    def test_has_basic_access(self):
        for perm, expected in (
            ("madc.basic_access", True),
            ("madc.corp_access", False),
        ):
            user = UserMainFactory(permissions__=[perm])
            self.assertEqual(General.objects.has_basic_access(user), expected)

    def test_has_corp_and_alliance_access(self):
        corp = UserMainFactory(permissions__=["madc.corp_access"])
        alliance = UserMainFactory(permissions__=["madc.alliance_access"])
        self.assertTrue(General.objects.has_corp_access(corp))
        self.assertFalse(General.objects.has_corp_access(alliance))
        self.assertTrue(General.objects.has_alliance_access(alliance))
        self.assertFalse(General.objects.has_alliance_access(corp))

    def test_has_admin_and_full_access(self):
        admin = UserMainFactory(permissions__=["madc.admin_access"])
        manager = UserMainFactory(permissions__=["madc.manage_access"])
        self.assertTrue(General.objects.has_admin_access(admin))
        self.assertFalse(General.objects.has_admin_access(manager))
        self.assertTrue(General.objects.has_full_access(admin))
        self.assertFalse(General.objects.has_full_access(manager))
        self.assertTrue(General.objects.has_full_access(self.superuser))


class TestSkillListAccess(AuthTestCase):
    """The access querysets get their rules from General.objects."""

    def test_full_access_sees_all_characters(self):
        # Alliance Auth
        from allianceauth.eveonline.models import EveCharacter

        admin = UserMainFactory(permissions__=["madc.admin_access"])
        total = EveCharacter.objects.count()
        for user in (admin, self.superuser):
            self.assertEqual(
                SkillList.objects.visible_eve_characters(user).count(), total
            )
            self.assertEqual(SkillList.objects.manage_to(user).count(), total)

    def test_basic_user_sees_only_own_characters(self):
        user = UserMainFactory(permissions__=["madc.basic_access"])
        visible = SkillList.objects.visible_eve_characters(user)
        self.assertEqual(
            list(visible.values_list("pk", flat=True)),
            [user.profile.main_character.pk],
        )
        self.assertEqual(SkillList.objects.manage_to(user).count(), 0)

    def test_manager_sees_own_characters_only_to_manage(self):
        user = UserMainFactory(permissions__=["madc.manage_access"])
        manageable = SkillList.objects.manage_to(user)
        self.assertEqual(
            list(manageable.values_list("pk", flat=True)),
            [user.profile.main_character.pk],
        )
