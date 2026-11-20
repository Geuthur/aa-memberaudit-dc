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
    ("react_base", {}, "get", None),
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

    def test_legacy_urls_should_redirect_to_the_react_page(self):
        self.client.force_login(self.user)
        cases = {
            "view/index/": "",
            "123/view/checker/": "doctrine/123/",
            "0/view/checker/": "doctrine/",
            "456/view/corporation_checker/": "corporation/456/",
            "0/view/corporation_checker/": "corporation/",
            "123/view/overview/": "overview/",
            "123/view/corporation_overview/": "overview/",
            "123/view/add/": "manage/",
            "123/view/administration/": "manage/",
        }
        for old, new in cases.items():
            with self.subTest(path=old):
                response = self.client.get(f"/{__app_name__}/{old}")
                self.assertRedirects(
                    response,
                    f"/{__app_name__}/{new}",
                    fetch_redirect_response=False,
                )

    def test_react_routes_should_render_the_react_page(self):
        # The catch-all serves the React page for every route of the frontend
        self.client.force_login(self.user)
        for path in ["", "doctrine/1/", "corporation/", "overview/", "manage/"]:
            with self.subTest(path=path):
                response = self.client.get(f"/{__app_name__}/{path}")
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertContains(response, "aa-memberaudit-dc-root")
