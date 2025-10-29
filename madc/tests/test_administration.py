"""TestView class."""

# Standard Library
import json
from http import HTTPStatus

# Django
from django.test import RequestFactory, TestCase
from django.urls import reverse

# Alliance Auth (External Libs)
from app_utils.testing import create_user_from_evecharacter

# AA Memberaudit Doctrine Checker
from madc import views
from madc.models.skillchecker import SkillList
from madc.tests.testdata.load_allianceauth import load_allianceauth
from madc.tests.testdata.load_eveuniverse import load_eveuniverse


class TestAdministrationView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_eveuniverse()

        cls.factory = RequestFactory()
        cls.user_admin_access, cls.character_ownership_admin = (
            create_user_from_evecharacter(
                character_id=1003,
                permissions=[
                    "madc.basic_access",
                    "madc.corp_access",
                    "madc.admin_access",
                ],
            )
        )
        cls.user_no_access, cls.character_ownership_no_access = (
            create_user_from_evecharacter(
                character_id=1004,
                permissions=[],
            )
        )
        cls.skill_plan = SkillList.objects.create(
            name="Test Skillplan",
            category="Test Category",
            active=True,
            ordering=1,
            skill_list='{"Test Level 1": 1, "Test Level 5": 5, "Test Level 3": 3}',
        )

    def test_edit_doctrine_name(self):
        """Test should edit doctrine name."""
        # given
        form_data = {"name": "name", "value": "New Doctrine Name"}
        # when
        request = self.factory.post(
            reverse("madc:update_skilllist", args=[self.skill_plan.pk]),
            data=form_data,
        )

        request.user = self.user_admin_access

        response = views.edit_doctrine(request, pk=self.skill_plan.pk)
        response_data = json.loads(response.content)

        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response_data["message"],
            "Name updated successfully",
        )

    def test_edit_doctrine_active(self):
        """Test should edit doctrine active status."""
        # given
        form_data = {"name": "active", "value": "false"}
        # when
        request = self.factory.post(
            reverse("madc:update_skilllist", args=[self.skill_plan.pk]),
            data=form_data,
        )

        request.user = self.user_admin_access

        response = views.edit_doctrine(request, pk=self.skill_plan.pk)
        response_data = json.loads(response.content)

        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response_data["message"],
            "Active status updated successfully",
        )
        self.skill_plan.refresh_from_db()
        self.assertFalse(self.skill_plan.active)

    def test_edit_doctrine_ordering(self):
        """Test should edit doctrine ordering."""
        # given
        form_data = {"name": "ordering", "value": "5"}
        # when
        request = self.factory.post(
            reverse("madc:update_skilllist", args=[self.skill_plan.pk]),
            data=form_data,
        )

        request.user = self.user_admin_access

        response = views.edit_doctrine(request, pk=self.skill_plan.pk)
        response_data = json.loads(response.content)

        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response_data["message"],
            "Ordering updated successfully",
        )
        self.skill_plan.refresh_from_db()
        self.assertEqual(self.skill_plan.ordering, 5)

    def test_edit_doctrine_category(self):
        """Test should edit doctrine category."""
        # given
        form_data = {"name": "category", "value": "New Category"}
        # when
        request = self.factory.post(
            reverse("madc:update_skilllist", args=[self.skill_plan.pk]),
            data=form_data,
        )

        request.user = self.user_admin_access

        response = views.edit_doctrine(request, pk=self.skill_plan.pk)
        response_data = json.loads(response.content)

        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response_data["message"],
            "Category updated successfully",
        )
        self.skill_plan.refresh_from_db()
        self.assertEqual(self.skill_plan.category, "New Category")

    def test_edit_doctrine_no_permission(self):
        """Test should not edit doctrine without permission."""
        # given
        form_data = {"name": "name", "value": "New Doctrine Name"}
        # when
        request = self.factory.post(
            reverse("madc:update_skilllist", args=[self.skill_plan.pk]),
            data=form_data,
        )

        request.user = self.user_no_access

        response = views.edit_doctrine(request, pk=self.skill_plan.pk)

        # then
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
