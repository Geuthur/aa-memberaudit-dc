"""TestView class."""

# Standard Library
from http import HTTPStatus
from unittest.mock import patch

# Django
from django.urls import reverse

# AA Memberaudit Doctrine Checker
from madc import views
from madc.tests import AuthTestCase
from madc.tests.testdata.app import UserMainFactory
from madc.tests.testdata.load_eveuniverse import load_eveuniverse

INDEX_PATH = "madc.views"


class TestViewIndexAccess(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_eveuniverse()

        cls.user_corp_access = UserMainFactory(
            permissions__=["madc.basic_access", "madc.corp_access"]
        )
        cls.user_admin_access = UserMainFactory(
            permissions__=[
                "madc.basic_access",
                "madc.corp_access",
                "madc.admin_access",
            ]
        )

    def test_index_view(self):
        """Test should load index view."""
        # given
        request = self.factory.get(reverse("madc:index"))
        request.user = self.user
        # when
        response = views.index(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_checker_view(self):
        """Test should load checker view."""
        # given
        request = self.factory.get(
            reverse(
                "madc:checker", args=[self.user.profile.main_character.character_id]
            )
        )
        request.user = self.user
        # when
        response = views.checker(
            request, character_id=self.user.profile.main_character.character_id
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_corporation_checker_view(self):
        """Test should load corporation checker view."""
        # given
        request = self.factory.get(
            reverse(
                "madc:corporation_checker",
                args=[
                    self.user_corp_access.profile.main_character.corporation.corporation_id
                ],
            )
        )
        request.user = self.user_corp_access
        # when
        response = views.corporation_checker(
            request,
            corporation_id=self.user_corp_access.profile.main_character.corporation.corporation_id,
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_overview_view(self):
        """Test should load overview view."""
        # given
        request = self.factory.get(
            reverse(
                "madc:overview", args=[self.user.profile.main_character.character_id]
            )
        )
        request.user = self.user
        # when
        response = views.overview(
            request, character_id=self.user.profile.main_character.character_id
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_administration_view(self):
        """Test should load administration view."""
        # given
        request = self.factory.get(
            reverse(
                "madc:administration",
                args=[self.user_admin_access.profile.main_character.character_id],
            )
        )
        request.user = self.user_admin_access
        # when
        response = views.administration(
            request,
            character_id=self.user_admin_access.profile.main_character.character_id,
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_add_doctrine_view(self):
        """Test should load add doctrine view."""
        # given
        request = self.factory.get(
            reverse(
                "madc:add_doctrine",
                args=[self.user_admin_access.profile.main_character.character_id],
            )
        )
        request.user = self.user_admin_access
        # when
        response = views.doctrine(
            request,
            character_id=self.user_admin_access.profile.main_character.character_id,
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @patch(INDEX_PATH + ".messages")
    def test_ajax_doctrine_view(self, mock_messages):
        """Test should load ajax doctrine view."""
        # given
        form_data = {
            "name": "Test Skillplan",
            "ordering": 1,
            "category": "Test Category",
            "skill_list": "Test Level 1\nTest Level 5\nTest Level 3",
        }
        # when
        request = self.factory.post(
            reverse("madc:ajax_doctrine"),
            data=form_data,
        )

        request.user = self.user_admin_access

        response = views.ajax_doctrine(request)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.success.assert_called_once()

    @patch(INDEX_PATH + ".messages")
    def test_ajax_doctrine_view_error(self, mock_messages):
        """Test should load ajax doctrine view with error."""
        # given
        form_data = {}
        # when
        request = self.factory.post(
            reverse("madc:ajax_doctrine"),
            data=form_data,
        )

        request.user = self.user_admin_access

        response = views.ajax_doctrine(request)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_once()

    @patch(INDEX_PATH + ".messages")
    def test_ajax_doctrine_view_wrong_parsed_skills(self, mock_messages):
        """Test should load ajax doctrine view with wrong parsed skills."""
        # given
        form_data = {
            "name": "Test Skillplan",
            "ordering": 1,
            "category": "Test Category",
            "skill_list": "Invalid Skill Format",
        }
        # when
        request = self.factory.post(
            reverse("madc:ajax_doctrine"),
            data=form_data,
        )

        request.user = self.user_admin_access

        response = views.ajax_doctrine(request)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        mock_messages.error.assert_called_with(
            request,
            "There was an error with your skill plan: Skill List (Skillplan format): Line 1: 'Invalid Skill Format' - Invalid format. Use 'Skill Name Level' (Level 1-5) or EVE localized format",
        )
