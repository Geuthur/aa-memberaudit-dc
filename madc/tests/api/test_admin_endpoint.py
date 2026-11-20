"""TestAPI class."""

# Standard Library
import json
from http import HTTPStatus

# Django
from django.urls import reverse

# Alliance Auth
from allianceauth.eveonline.models import EveCorporationInfo

# Alliance Auth (External Libs)
from eveuniverse.models import EveType
from memberaudit.models import Character

# AA Memberaudit Doctrine Checker
from madc.models.skillchecker import SkillList
from madc.tests import AuthTestCase
from madc.tests.testdata.app import UserMainFactory
from madc.tests.testdata.load_eveuniverse import load_eveuniverse
from madc.tests.testdata.load_memberaudit import create_memberaudit

API_URL = "madc:api"


class TestAdminAPI(AuthTestCase):
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
        cls.user_no_access = UserMainFactory(permissions__=[])
        for user in [
            cls.user,
            cls.superuser,
            cls.user_corp_access,
            cls.user_admin_access,
            cls.user_no_access,
        ]:
            create_memberaudit(user.profile.main_character)

        cls.eve_type = EveType.objects.get(id=17940)
        cls.skill_list = SkillList.objects.create(
            name="Test Skill List",
            category="Test Category",
            active=True,
            skill_list=json.dumps({str(cls.eve_type.name): 5}),
            ordering=1,
        )

    def test_account_overview_endpoint(self):
        # given
        url = reverse(f"{API_URL}:get_account_overview")
        self.client.force_login(self.user)
        # when
        response = self.client.get(url)
        response_json = response.json()
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response_json), 1)

    def test_account_overview_endpoint_admin_access(self):
        # given
        url = reverse(f"{API_URL}:get_account_overview")
        self.client.force_login(self.user_admin_access)
        # when
        response = self.client.get(url)
        response_json = response.json()

        all_characters = Character.objects.count()
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response_json), all_characters)

    def test_account_overview_should_return_403_without_basic_access(self):
        # given
        url = reverse(f"{API_URL}:get_account_overview")
        self.client.force_login(self.user_no_access)
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), {"error": "Permission Denied"})

    def test_corporation_overview_endpoint(self):
        # given
        url = reverse(f"{API_URL}:get_corporation_overview")
        self.client.force_login(self.user_corp_access)
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

    def test_corporation_overview_should_return_403_without_basic_access(self):
        # given
        url = reverse(f"{API_URL}:get_corporation_overview")
        self.client.force_login(self.user_no_access)
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), {"error": "Permission Denied"})
