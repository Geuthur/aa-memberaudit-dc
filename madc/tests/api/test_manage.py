"""Tests for the manage endpoints: skill lists and overviews."""

# Standard Library
import json
from http import HTTPStatus

# Django
from django.urls import reverse

# Alliance Auth
from allianceauth.tests.auth_utils import AuthUtils

# AA Memberaudit Doctrine Checker
from madc.models.skillchecker import SkillList
from madc.tests import AuthTestCase
from madc.tests.testdata.app import UserMainFactory
from madc.tests.testdata.load_memberaudit import create_memberaudit

API_URL = "madc:api"
PERMISSION_DENIED = {"error": "Permission Denied"}


class ManageTestCase(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = UserMainFactory(
            permissions__=["madc.basic_access", "madc.manage_access"]
        )

    def setUp(self):
        self.skill_list = SkillList.objects.create(
            name="Fleet",
            category="Combat",
            ordering=5,
            active=True,
            skill_list=json.dumps({"Mining Barge": 5, "Gunnery": 3}),
        )
        self.client.force_login(self.manager)

    def _put(self, pk: int, payload: dict):
        return self.client.put(
            reverse(f"{API_URL}:update_skilllist", kwargs={"pk": pk}),
            data=payload,
            content_type="application/json",
        )


class TestManageList(ManageTestCase):
    def test_manage_should_list_skill_lists(self):
        # when
        response = self.client.get(reverse(f"{API_URL}:manage_skilllists"))
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.json(),
            [
                {
                    "id": self.skill_list.pk,
                    "name": "Fleet",
                    "category": "Combat",
                    "ordering": 5,
                    "active": True,
                    "skill_count": 2,
                }
            ],
        )

    def test_manage_should_return_403_without_manage_access(self):
        # given
        self.client.force_login(self.user)
        # when
        response = self.client.get(reverse(f"{API_URL}:manage_skilllists"))
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), PERMISSION_DENIED)


class TestManageCreate(ManageTestCase):
    def _post(self, payload: dict):
        return self.client.post(
            reverse(f"{API_URL}:create_skilllist"),
            data=payload,
            content_type="application/json",
        )

    def test_create_should_store_parsed_skill_plan(self):
        # when
        response = self._post(
            {
                "name": "Logistics",
                "category": "Support",
                "ordering": 3,
                "skill_list": "Mining Barge 3\nMining Barge 4\n"
                '<localized hint="Gunnery">Gunnery*</localized> 2',
            }
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        created = SkillList.objects.get(name="Logistics")
        self.assertEqual(created.get_skills(), {"Mining Barge": 4, "Gunnery": 2})
        self.assertEqual(created.category, "Support")
        self.assertEqual(created.ordering, 3)
        self.assertTrue(created.active)
        self.assertEqual(response.json()["skill_count"], 2)

    def test_create_should_return_400_for_invalid_format(self):
        # when
        response = self._post({"name": "Broken", "skill_list": "Mining Barge"})
        # then
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("Invalid format", response.json()["error"])
        self.assertFalse(SkillList.objects.filter(name="Broken").exists())

    def test_create_should_return_400_for_existing_name(self):
        # when
        response = self._post({"name": "Fleet", "skill_list": "Gunnery 1"})
        # then
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("already exists", response.json()["error"])

    def test_create_should_return_400_for_existing_name_in_other_case(self):
        # when
        response = self._post({"name": "FLEET", "skill_list": "Gunnery 1"})
        # then
        # MySQL compares case-insensitively, there the form already rejects it
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("already exists", response.json()["error"])
        self.assertEqual(SkillList.objects.filter(name__iexact="fleet").count(), 1)

    def test_create_should_return_403_without_manage_access(self):
        # given
        self.client.force_login(self.user)
        # when
        response = self._post({"name": "New", "skill_list": "Gunnery 1"})
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertFalse(SkillList.objects.filter(name="New").exists())


class TestManageUpdate(ManageTestCase):
    def test_update_should_change_all_given_fields(self):
        # when
        response = self._put(
            self.skill_list.pk,
            {"name": " Fleet 2 ", "category": "PvP", "ordering": 7, "active": False},
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.skill_list.refresh_from_db()
        self.assertEqual(self.skill_list.name, "Fleet 2")
        self.assertEqual(self.skill_list.category, "PvP")
        self.assertEqual(self.skill_list.ordering, 7)
        self.assertFalse(self.skill_list.active)
        self.assertEqual(response.json()["active"], False)

    def test_update_should_keep_fields_not_given(self):
        # when
        response = self._put(self.skill_list.pk, {"active": False})
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.skill_list.refresh_from_db()
        self.assertEqual(self.skill_list.name, "Fleet")
        self.assertEqual(self.skill_list.ordering, 5)
        self.assertFalse(self.skill_list.active)

    def test_update_should_return_400_for_invalid_values(self):
        SkillList.objects.create(name="Other", skill_list="{}")
        cases = {
            "empty name": ({"name": "  "}, "Name cannot be empty"),
            "existing name": (
                {"name": "other"},
                "Skill list with this name already exists",
            ),
            "long name": ({"name": "x" * 51}, "Name can have at most 50 characters"),
            "long category": (
                {"category": "x" * 21},
                "Category can have at most 20 characters",
            ),
            "ordering too high": (
                {"ordering": 1000},
                "Ordering must be between 0 and 999",
            ),
            "ordering negative": (
                {"ordering": -1},
                "Ordering must be between 0 and 999",
            ),
        }
        for name, (payload, error) in cases.items():
            with self.subTest(case=name):
                response = self._put(self.skill_list.pk, payload)
                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
                self.assertEqual(response.json(), {"error": error})
        self.skill_list.refresh_from_db()
        self.assertEqual(self.skill_list.name, "Fleet")
        self.assertEqual(self.skill_list.ordering, 5)

    def test_update_should_remove_category_for_empty_text(self):
        for category in ["", "   "]:
            with self.subTest(category=category):
                self.skill_list.category = "Combat"
                self.skill_list.save()
                # when
                response = self._put(self.skill_list.pk, {"category": category})
                # then
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertIsNone(response.json()["category"])
                self.skill_list.refresh_from_db()
                self.assertIsNone(self.skill_list.category)

    def test_manage_should_list_skill_list_without_skills(self):
        SkillList.objects.create(name="Empty", skill_list="")
        # when
        response = self.client.get(reverse(f"{API_URL}:manage_skilllists"))
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        counts = {entry["name"]: entry["skill_count"] for entry in response.json()}
        self.assertEqual(counts["Empty"], 0)

    def test_update_should_return_404_for_unknown_skill_list(self):
        response = self._put(self.skill_list.pk + 100, {"active": False})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.json(), {"error": "Skill list not found"})

    def test_update_should_return_403_without_manage_access(self):
        # given
        self.client.force_login(self.user)
        # when
        response = self._put(self.skill_list.pk, {"active": False})
        # then
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.skill_list.refresh_from_db()
        self.assertTrue(self.skill_list.active)


class TestManageDelete(ManageTestCase):
    def _delete(self, pk: int):
        return self.client.delete(
            reverse(f"{API_URL}:delete_skilllist", kwargs={"pk": pk})
        )

    def test_delete_should_remove_skill_list(self):
        response = self._delete(self.skill_list.pk)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), {"message": "Skilllist: Fleet deleted"})
        self.assertFalse(SkillList.objects.filter(pk=self.skill_list.pk).exists())

    def test_delete_should_return_404_for_unknown_skill_list(self):
        response = self._delete(self.skill_list.pk + 100)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_delete_should_return_403_without_manage_access(self):
        self.client.force_login(self.user)
        response = self._delete(self.skill_list.pk)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(SkillList.objects.filter(pk=self.skill_list.pk).exists())


class TestOverviews(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_memberaudit(cls.user.profile.main_character)
        # The corporation overview needs corp_access for the own corporation
        cls.user = AuthUtils.add_permission_to_user_by_name(
            "madc.corp_access", cls.user
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_account_overview_should_return_flat_characters_with_actions(self):
        # given
        main = self.user.profile.main_character
        # when
        response = self.client.get(reverse(f"{API_URL}:get_account_overview"))
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["character_id"], main.character_id)
        self.assertEqual(data[0]["character_name"], main.character_name)
        self.assertEqual(data[0]["actions"], f"/doctrine/{main.character_id}/")
        self.assertIn(str(main.character_id), data[0]["character_icon"])

    def test_corporation_overview_should_return_flat_corporations_with_actions(
        self,
    ):
        # given
        corporation_id = self.user.profile.main_character.corporation_id
        # when
        response = self.client.get(reverse(f"{API_URL}:get_corporation_overview"))
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["corporation_id"], corporation_id)
        self.assertEqual(data[0]["actions"], f"/corporation/{corporation_id}/")
        self.assertIn(str(corporation_id), data[0]["corporation_icon"])
