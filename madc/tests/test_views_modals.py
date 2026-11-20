"""Tests for the transitional modal views of the jQuery pages."""

# Standard Library
import json
from http import HTTPStatus

# Django
from django.urls import reverse

# Alliance Auth (External Libs)
from eveuniverse.models import EveType
from memberaudit.models import CharacterSkill

# AA Memberaudit Doctrine Checker
from madc.models.skillchecker import SkillList
from madc.tests import AuthTestCase
from madc.tests.testdata.app import UserMainFactory
from madc.tests.testdata.load_eveuniverse import load_eveuniverse
from madc.tests.testdata.load_memberaudit import create_memberaudit


class TestModalViews(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_eveuniverse()
        cls.main = cls.user.profile.main_character
        CharacterSkill.objects.create(
            character=create_memberaudit(cls.main),
            eve_type=EveType.objects.get(id=17940),
            active_skill_level=3,
            skillpoints_in_skill=1000,
            trained_skill_level=3,
        )
        cls.other = UserMainFactory()
        cls.skill_list = SkillList.objects.create(
            name="Fleet", skill_list=json.dumps({"Gunnery": 3})
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_missing_skills_modal_should_render_skills(self):
        response = self.client.get(
            reverse(
                "madc:missing_skills_modal",
                kwargs={
                    "character_id": self.main.character_id,
                    "pk": self.skill_list.pk,
                },
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Gunnery")

    def test_missing_skills_modal_should_return_403_for_foreign_character(self):
        response = self.client.get(
            reverse(
                "madc:missing_skills_modal",
                kwargs={
                    "character_id": self.other.profile.main_character.character_id,
                    "pk": self.skill_list.pk,
                },
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_missing_skills_modal_should_return_403_without_character_skills(self):
        # given: a character of the user without Member Audit data
        character = UserMainFactory().profile.main_character
        character.character_ownership.user = self.user
        character.character_ownership.save()
        # when
        response = self.client.get(
            reverse(
                "madc:missing_skills_modal",
                kwargs={
                    "character_id": character.character_id,
                    "pk": self.skill_list.pk,
                },
            )
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_doctrine_skills_modal_should_render_skill_list(self):
        response = self.client.get(
            reverse("madc:doctrine_skills_modal", kwargs={"pk": self.skill_list.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Fleet")
