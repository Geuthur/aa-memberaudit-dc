"""Every view requires `basic_access`, higher permissions do not replace it."""

# Standard Library
from http import HTTPStatus

# Django
from django.urls import reverse

# AA Memberaudit Doctrine Checker
from madc import __app_name__
from madc.models.general import General
from madc.tests import AuthTestCase
from madc.tests.testdata.app import UserMainFactory

BASIC_ACCESS = f"{__app_name__}.basic_access"
HIGHER_PERMISSIONS = [
    f"{__app_name__}.{codename}"
    for codename, _ in General._meta.permissions
    if codename != "basic_access"
]

# (url name, kwargs, method, permissions of which one is needed besides basic_access)
VIEWS = [
    ("index", {}, "get", None),
    ("checker", {"character_id": 1}, "get", None),
    ("overview", {"character_id": 1}, "get", None),
    ("corporation_checker", {"corporation_id": 1}, "get", ["corp_access"]),
    ("corporation_overview", {"character_id": 1}, "get", ["corp_access"]),
    (
        "administration",
        {"character_id": 1},
        "get",
        ["manage_access", "admin_access"],
    ),
    ("add_doctrine", {"character_id": 1}, "get", ["manage_access", "admin_access"]),
    ("ajax_doctrine", {}, "post", ["manage_access", "admin_access"]),
    ("delete_doctrine", {}, "post", ["manage_access", "admin_access"]),
    ("update_skilllist", {"pk": 1}, "post", ["manage_access", "admin_access"]),
]


class TestViewsBasicAccess(AuthTestCase):
    def _call(self, user, name, kwargs, method):
        self.client.force_login(user)
        return getattr(self.client, method)(reverse(f"madc:{name}", kwargs=kwargs))

    def _denied(self, response):
        # `permissions_required` redirects to the login page
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn("login", response["Location"])

    def test_views_should_deny_without_basic_access(self):
        users = {"no permission": UserMainFactory(permissions__=[])}
        users["all higher permissions"] = UserMainFactory(
            permissions__=HIGHER_PERMISSIONS
        )
        for permission in HIGHER_PERMISSIONS:
            users[permission] = UserMainFactory(permissions__=[permission])

        for name, kwargs, method, _needed in VIEWS:
            for label, user in users.items():
                with self.subTest(view=name, user=label):
                    self._denied(self._call(user, name, kwargs, method))

    def test_views_should_deny_with_basic_access_only_if_higher_permission_needed(
        self,
    ):
        user = UserMainFactory(permissions__=[BASIC_ACCESS])
        for name, kwargs, method, needed in VIEWS:
            if needed is None:
                continue
            with self.subTest(view=name):
                self._denied(self._call(user, name, kwargs, method))

    def test_views_should_pass_with_basic_access_and_needed_permission(self):
        for name, kwargs, method, needed in VIEWS:
            for permission in needed or [None]:
                perms = [BASIC_ACCESS] + ([f"madc.{permission}"] if permission else [])
                user = UserMainFactory(permissions__=perms)
                with self.subTest(view=name, permission=permission):
                    response = self._call(user, name, kwargs, method)
                    # The view itself answers (200, redirect to the app, 4xx of its own)
                    if response.status_code == HTTPStatus.FOUND:
                        self.assertNotIn("login", response["Location"])
