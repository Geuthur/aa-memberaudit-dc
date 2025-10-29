"""TestAPI class."""

# Standard Library
import json
from http import HTTPStatus

# Django
from django.test import RequestFactory, TestCase
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import EveCorporationInfo

# Alliance Auth (External Libs)
from app_utils.testing import create_user_from_evecharacter
from eveuniverse.models import EveType
from memberaudit.models import Character

# AA Memberaudit Doctrine Checker
from madc.models.skillchecker import SkillList
from madc.tests.testdata.load_allianceauth import load_allianceauth
from madc.tests.testdata.load_eveuniverse import load_eveuniverse
from madc.tests.testdata.load_memberaudit import load_memberaudit

API_PATH = "madc.api.admin"
API_URL = "madc:api"


class TestAdminAPI(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_eveuniverse()
        load_memberaudit()

        cls.factory = RequestFactory()
        cls.user, cls.character_ownership = create_user_from_evecharacter(
            character_id=1001,
            permissions=["madc.basic_access"],
        )
        cls.user_corp_access, cls.character_ownership_corp = (
            create_user_from_evecharacter(
                character_id=1002,
                permissions=["madc.basic_access", "madc.corp_access"],
            )
        )
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

        cls.eve_type = EveType.objects.get(id=17940)
        cls.memberaudit = Character.objects.get(eve_character__character_id=1001)
        cls.skill_list = SkillList.objects.create(
            name="Test Skill List",
            category="Test Category",
            active=True,
            skill_list=json.dumps({str(cls.eve_type.name): 5}),
            ordering=1,
        )

    def test_admin_endpoint_access(self):
        # given
        url = reverse(f"{API_URL}:admin_doctrines")
        self.client.force_login(self.user_admin_access)
        # when
        response = self.client.get(url)
        response_json = response.json()
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("Test Skill List", response_json)
        self.assertIn(
            "Test Category", response_json["Test Skill List"]["category"]["html"]
        )

    def test_admin_endpoint_no_access(self):
        # given
        url = reverse(f"{API_URL}:admin_doctrines")
        self.client.force_login(self.user_no_access)
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_character_overview_endpoint(self):
        # given
        url = reverse(f"{API_URL}:get_character_overview")
        self.client.force_login(self.user)
        # when
        response = self.client.get(url)
        response_json = response.json()
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response_json), 1)

    def test_character_overview_endpoint_admin_access(self):
        # given
        url = reverse(f"{API_URL}:get_character_overview")
        self.client.force_login(self.user_admin_access)
        # when
        response = self.client.get(url)
        response_json = response.json()

        all_characters = Character.objects.count()
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response_json), all_characters)

    def test_character_overview_no_access(self):
        # given
        url = reverse(f"{API_URL}:get_character_overview")
        self.client.force_login(self.user_no_access)
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_corporation_overview_endpoint(self):
        # given
        url = reverse(f"{API_URL}:get_corporation_overview")
        self.client.force_login(self.user)
        # when
        response = self.client.get(url)
        response_json = response.json()

        counted_corps = len(response_json)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(counted_corps, 1)

    def test_corporation_overview_endpoint_admin_access(self):
        # given
        url = reverse(f"{API_URL}:get_corporation_overview")
        self.client.force_login(self.user_admin_access)
        # when
        response = self.client.get(url)
        response_json = response.json()

        counted_corps = len(response_json)
        all_corps = EveCorporationInfo.objects.count()

        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(counted_corps, all_corps)

    def test_corporation_overview_no_access(self):
        # given
        url = reverse(f"{API_URL}:get_corporation_overview")
        self.client.force_login(self.user_no_access)
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
