"""Tests for the General permission helpers."""

# AA Memberaudit Doctrine Checker
from madc.models.general import General
from madc.tests import AuthTestCase
from madc.tests.testdata.app import UserMainFactory


class TestGeneralPermissions(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_basic = UserMainFactory(permissions__=["madc.basic_access"])
        cls.user_manage = UserMainFactory(permissions__=["madc.manage_access"])
        cls.user_admin = UserMainFactory(permissions__=["madc.admin_access"])

    def test_get_perm(self):
        for perm in General.Permission:
            self.assertEqual(General.get_perm(perm), f"madc.{perm.value}")
        self.assertEqual(General.get_perm("basic_access"), "madc.basic_access")

    def test_codenames_unchanged(self):
        self.assertEqual(
            [p.value for p in General.Permission],
            [
                "basic_access",
                "corp_access",
                "alliance_access",
                "manage_access",
                "admin_access",
            ],
        )
        self.assertEqual(
            [c for c, _ in General._meta.permissions],
            [p.value for p in General.Permission],
        )

    def test_has_perm(self):
        self.assertTrue(
            General.has_perm(self.user_basic, General.Permission.BASIC_ACCESS)
        )
        self.assertFalse(
            General.has_perm(self.user_basic, General.Permission.ADMIN_ACCESS)
        )
        self.assertFalse(General.has_perm(None, General.Permission.BASIC_ACCESS))

    def test_has_any_perm(self):
        self.assertTrue(
            General.has_any_perm(
                self.user_basic,
                General.Permission.ADMIN_ACCESS,
                General.Permission.BASIC_ACCESS,
            )
        )
        self.assertFalse(
            General.has_any_perm(self.user_basic, General.Permission.ADMIN_ACCESS)
        )

    def test_has_management_access(self):
        self.assertTrue(General.has_management_access(self.user_manage))
        self.assertTrue(General.has_management_access(self.user_admin))
        self.assertFalse(General.has_management_access(self.user_basic))
