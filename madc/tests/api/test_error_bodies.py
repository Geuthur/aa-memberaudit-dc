"""Error bodies of the endpoints themselves (not of `basic_access_required`)."""

# Standard Library
from http import HTTPStatus
from unittest.mock import patch

# Django
from django.urls import reverse

# AA Memberaudit Doctrine Checker
from madc.models.skillchecker import SkillList
from madc.tests import AuthTestCase
from madc.tests.testdata.app import UserMainFactory

API_URL = "madc:api"
PERMISSION_DENIED = {"error": "Permission Denied"}


class TestAdminErrorBodies(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = type(SkillList.objects)

    def test_account_overview_should_return_error_body_without_visible_characters(
        self,
    ):
        # given
        self.client.force_login(self.user)
        # when
        with patch.object(self.manager, "visible_eve_characters", return_value=None):
            response = self.client.get(reverse(f"{API_URL}:get_account_overview"))
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), PERMISSION_DENIED)

    def test_corporation_overview_should_return_error_body_without_visible_corporations(
        self,
    ):
        # given
        self.client.force_login(self.user)
        # when
        with patch.object(self.manager, "visible_eve_corporations", return_value=None):
            response = self.client.get(reverse(f"{API_URL}:get_corporation_overview"))
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), PERMISSION_DENIED)


class TestSkillCheckerErrorBodies(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other = UserMainFactory()
        cls.other_character_id = cls.other.profile.main_character.character_id
        cls.skill_list = SkillList.objects.create(
            name="Test Skill List", skill_list="{}", active=True
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_doctrines_should_return_error_body_for_foreign_character(self):
        # when
        response = self.client.get(
            reverse(
                f"{API_URL}:get_doctrines",
                kwargs={"character_id": self.other_character_id},
            )
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), PERMISSION_DENIED)

    def test_corporation_doctrines_should_return_error_body_for_unknown_corporation(
        self,
    ):
        # when
        response = self.client.get(
            reverse(
                f"{API_URL}:get_corporation_doctrines",
                kwargs={"corporation_id": 1},
            )
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), PERMISSION_DENIED)

    def test_missing_skills_should_return_error_body_for_foreign_character(self):
        # when
        response = self.client.get(
            reverse(
                f"{API_URL}:get_missing_skills",
                kwargs={"character_id": self.other_character_id, "pk": 1},
            )
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), PERMISSION_DENIED)
