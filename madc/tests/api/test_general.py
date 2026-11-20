"""Tests for the general endpoints: menu and user."""

# Standard Library
from http import HTTPStatus

# Django
from django.urls import reverse

# AA Memberaudit Doctrine Checker
from madc.tests import AuthTestCase
from madc.tests.testdata.app import UserMainFactory

API_URL = "madc:api"


class TestMenuEndpoint(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_corp_access = UserMainFactory(
            permissions__=["madc.basic_access", "madc.corp_access"]
        )
        cls.user_alliance_access = UserMainFactory(
            permissions__=["madc.basic_access", "madc.alliance_access"]
        )
        cls.user_admin_access = UserMainFactory(
            permissions__=["madc.basic_access", "madc.admin_access"]
        )
        cls.user_manage_access = UserMainFactory(
            permissions__=["madc.basic_access", "madc.manage_access"]
        )

    def _links(self, user) -> tuple[list[str], list[str]]:
        self.client.force_login(user)
        response = self.client.get(reverse(f"{API_URL}:get_menu"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        return (
            [link["link"] for link in data["left_links"]],
            [link["link"] for link in data["right_links"]],
        )

    def test_menu_should_show_basic_links_for_basic_access(self):
        left, right = self._links(self.user)
        self.assertEqual(left, ["/", "/overview/"])
        self.assertEqual(right, [])

    def test_menu_should_show_corporation_link_with_corp_access(self):
        left, right = self._links(self.user_corp_access)
        self.assertEqual(left, ["/", "/corporation/", "/overview/"])
        self.assertEqual(right, [])

    def test_menu_should_show_corporation_link_with_alliance_or_admin_access(self):
        for user in [self.user_alliance_access, self.user_admin_access]:
            with self.subTest(user=user):
                left, __ = self._links(user)
                self.assertEqual(left, ["/", "/corporation/", "/overview/"])

    def test_menu_should_show_manage_link_with_manage_access(self):
        __, right = self._links(self.user_manage_access)
        self.assertEqual(right, ["/manage/"])


class TestUserEndpoint(AuthTestCase):
    def test_user_should_return_main_character_and_permissions(self):
        # given
        self.client.force_login(self.user)
        main = self.user.profile.main_character
        # when
        response = self.client.get(reverse(f"{API_URL}:get_user"))
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(data["user_id"], self.user.pk)
        self.assertEqual(data["character_id"], main.character_id)
        self.assertEqual(data["character_name"], main.character_name)
        self.assertEqual(data["corporation_id"], main.corporation_id)
        self.assertIn(str(main.character_id), data["portrait"])
        self.assertFalse(data["is_admin"])
        self.assertEqual(
            data["permissions"],
            {
                "basic_access": True,
                "corp_access": False,
                "alliance_access": False,
                "manage_access": False,
                "admin_access": False,
            },
        )

    def test_user_should_mark_admin(self):
        # given
        admin = UserMainFactory(
            permissions__=["madc.basic_access", "madc.admin_access"]
        )
        self.client.force_login(admin)
        # when
        response = self.client.get(reverse(f"{API_URL}:get_user"))
        # then
        data = response.json()
        self.assertTrue(data["is_admin"])
        self.assertTrue(data["permissions"]["manage_access"])
