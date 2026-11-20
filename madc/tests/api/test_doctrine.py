"""Tests for the doctrine endpoints: skill check of accounts and corporations."""

# Standard Library
import json
from http import HTTPStatus

# Third Party
# AA EVE SDE Factory
from evesde_factory.allianceauth import EveCharacterFactory
from evesde_factory.utils import add_character_to_user

# Django
from django.core.cache import cache
from django.urls import reverse

# Alliance Auth
from allianceauth.tests.auth_utils import AuthUtils

# Alliance Auth (External Libs)
from eveuniverse.models import EveType
from memberaudit.models import CharacterSkill

# AA Memberaudit Doctrine Checker
from madc.models.skillchecker import SkillList
from madc.tests import AuthTestCase
from madc.tests.testdata.app import UserMainFactory
from madc.tests.testdata.load_eveuniverse import load_eveuniverse
from madc.tests.testdata.load_memberaudit import create_memberaudit

API_URL = "madc:api"
PERMISSION_DENIED = {"error": "Permission Denied"}


class DoctrineTestCase(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_eveuniverse()
        cls.main = cls.user.profile.main_character
        cls.alt = EveCharacterFactory(
            corporation_id=cls.main.corporation_id,
            corporation_name=cls.main.corporation_name,
        )
        add_character_to_user(cls.user, cls.alt)
        cls.memberaudit_main = create_memberaudit(cls.main)
        cls.memberaudit_alt = create_memberaudit(cls.alt)

        cls.eve_type = EveType.objects.get(id=17940)
        # Main has trained the skill to 3, alt to 5
        CharacterSkill.objects.create(
            character=cls.memberaudit_main,
            eve_type=cls.eve_type,
            active_skill_level=3,
            skillpoints_in_skill=1000,
            trained_skill_level=3,
        )
        CharacterSkill.objects.create(
            character=cls.memberaudit_alt,
            eve_type=cls.eve_type,
            active_skill_level=5,
            skillpoints_in_skill=1000,
            trained_skill_level=5,
        )

        cls.other = UserMainFactory()
        cls.other_main = cls.other.profile.main_character

        cls.mining = SkillList.objects.create(
            name="Mining",
            category="Industry",
            ordering=1,
            skill_list=json.dumps({cls.eve_type.name: 4}),
        )
        cls.combat = SkillList.objects.create(
            name="Combat",
            category="PvP",
            ordering=2,
            skill_list=json.dumps({cls.eve_type.name: 2, "Gunnery": 1}),
        )
        cls.hidden = SkillList.objects.create(
            name="Hidden",
            category="PvP",
            ordering=3,
            active=False,
            skill_list=json.dumps({cls.eve_type.name: 1}),
        )

    def setUp(self):
        cache.clear()
        self.client.force_login(self.user)


class TestAccountDoctrines(DoctrineTestCase):
    def test_doctrines_should_return_active_doctrines_per_character(self):
        # when
        response = self.client.get(
            reverse(
                f"{API_URL}:get_doctrines",
                kwargs={"character_id": self.main.character_id},
            )
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        by_character = {
            entry["character"]["character_id"]: entry["doctrines"]
            for entry in response.json()
        }
        self.assertEqual(
            set(by_character), {self.main.character_id, self.alt.character_id}
        )
        main_doctrines = by_character[self.main.character_id]
        self.assertEqual(set(main_doctrines), {"Mining", "Combat"})
        self.assertEqual(
            main_doctrines["Mining"],
            {
                "id": self.mining.pk,
                "name": "Mining",
                "category": "Industry",
                "order": 1,
                "skills": [{"skill_name": self.eve_type.name, "required_level": 4}],
            },
        )
        self.assertEqual(by_character[self.alt.character_id]["Mining"]["skills"], [])

    def test_doctrines_should_return_403_for_foreign_character(self):
        response = self.client.get(
            reverse(
                f"{API_URL}:get_doctrines",
                kwargs={"character_id": self.other_main.character_id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), PERMISSION_DENIED)

    def test_doctrines_should_return_character_without_owner(self):
        # given: only an admin sees a character without owner
        admin = UserMainFactory(
            permissions__=["madc.basic_access", "madc.admin_access"]
        )
        orphan = EveCharacterFactory()
        SkillList.objects.create(name="Empty", skill_list="")
        self.client.force_login(admin)
        # when
        response = self.client.get(
            reverse(
                f"{API_URL}:get_doctrines",
                kwargs={"character_id": orphan.character_id},
            )
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["character"]["character_id"], orphan.character_id)
        self.assertEqual(data[0]["doctrines"], {})

    def test_doctrines_should_treat_skill_list_without_skills_as_fulfilled(self):
        SkillList.objects.create(name="Empty", skill_list="")
        # when
        response = self.client.get(
            reverse(
                f"{API_URL}:get_doctrines",
                kwargs={"character_id": self.main.character_id},
            )
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()[0]["doctrines"]["Empty"]["skills"], [])

    def test_doctrines_should_return_403_for_unknown_character(self):
        response = self.client.get(
            reverse(f"{API_URL}:get_doctrines", kwargs={"character_id": 1})
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class TestCorporationDoctrines(DoctrineTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The corporation endpoints need corp_access for the own corporation
        cls.user = AuthUtils.add_permission_to_user_by_name(
            "madc.corp_access", cls.user
        )

    def test_members_should_return_mains_with_corp_alts_and_active_doctrines(self):
        # when
        response = self.client.get(
            reverse(
                f"{API_URL}:get_corporation_members_list",
                kwargs={"corporation_id": self.main.corporation_id},
            )
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(data["corporation_id"], self.main.corporation_id)
        self.assertEqual(len(data["members"]), 1)
        member = data["members"][0]
        self.assertEqual(member["character"]["character_id"], self.main.character_id)
        self.assertEqual(
            [alt["character_id"] for alt in member["alts"]], [self.alt.character_id]
        )
        self.assertEqual(
            data["doctrines"],
            [
                {
                    "id": self.mining.pk,
                    "name": "Mining",
                    "category": "Industry",
                    "order": 1,
                },
                {"id": self.combat.pk, "name": "Combat", "category": "PvP", "order": 2},
            ],
        )

    def test_members_should_return_403_for_foreign_corporation(self):
        response = self.client.get(
            reverse(
                f"{API_URL}:get_corporation_members_list",
                kwargs={"corporation_id": self.other_main.corporation_id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_corporation_doctrines_should_take_best_character_of_account(self):
        # when
        response = self.client.get(
            reverse(
                f"{API_URL}:get_corporation_doctrines",
                kwargs={"corporation_id": self.main.corporation_id},
            )
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        doctrines = data[0]["doctrines"]
        self.assertEqual(set(doctrines), {"Mining", "Combat"})
        # The alt has Mining Barge 5, so nothing is missing for Mining
        self.assertEqual(doctrines["Mining"]["skills"], [])

    def test_corporation_doctrines_should_filter_by_category(self):
        response = self.client.get(
            reverse(
                f"{API_URL}:get_corporation_doctrines",
                kwargs={"corporation_id": self.main.corporation_id},
            ),
            {"category": "PvP"},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(set(response.json()[0]["doctrines"]), {"Combat"})

    def test_audit_members_should_filter_by_doctrine_ids(self):
        # when
        response = self.client.post(
            reverse(
                f"{API_URL}:audit_corporation_members",
                kwargs={"corporation_id": self.main.corporation_id},
            ),
            data={
                "character_ids": [self.main.character_id],
                "doctrine_ids": [self.mining.pk, self.hidden.pk],
            },
            content_type="application/json",
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        # Inactive skill lists stay hidden even if requested
        self.assertEqual(set(data[0]["doctrines"]), {"Mining"})

    def test_audit_members_should_return_empty_list_for_no_characters(self):
        response = self.client.post(
            reverse(
                f"{API_URL}:audit_corporation_members",
                kwargs={"corporation_id": self.main.corporation_id},
            ),
            data={"character_ids": []},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), [])

    def test_audit_members_should_return_403_for_foreign_corporation(self):
        response = self.client.post(
            reverse(
                f"{API_URL}:audit_corporation_members",
                kwargs={"corporation_id": self.other_main.corporation_id},
            ),
            data={},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class TestSkillDetails(DoctrineTestCase):
    def test_missing_skills_should_list_missing_skills_with_clipboard(self):
        # when
        response = self.client.get(
            reverse(
                f"{API_URL}:get_missing_skills",
                kwargs={"character_id": self.main.character_id, "pk": self.combat.pk},
            )
        )
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.json(),
            {
                "character_id": self.main.character_id,
                "character_name": self.main.character_name,
                "doctrine_id": self.combat.pk,
                "doctrine_name": "Combat",
                "missing_skills": [
                    {"name": "Gunnery", "trained_level": 0, "needed_level": 1}
                ],
                "clipboard_export": "Gunnery 1",
            },
        )

    def test_missing_skills_should_count_active_level(self):
        # given: trained 5 but only 3 active (e.g. alpha clone)
        skill = CharacterSkill.objects.get(character=self.memberaudit_main)
        skill.trained_skill_level = 5
        skill.save()
        # when
        response = self.client.get(
            reverse(
                f"{API_URL}:get_missing_skills",
                kwargs={"character_id": self.main.character_id, "pk": self.mining.pk},
            )
        )
        # then
        self.assertEqual(
            response.json()["missing_skills"],
            [{"name": self.eve_type.name, "trained_level": 3, "needed_level": 4}],
        )

    def test_missing_skills_should_return_404_for_unknown_skill_list(self):
        response = self.client.get(
            reverse(
                f"{API_URL}:get_missing_skills",
                kwargs={"character_id": self.main.character_id, "pk": 9999},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.json(), {"error": "Skill list not found"})

    def test_missing_skills_should_return_403_for_foreign_character(self):
        response = self.client.get(
            reverse(
                f"{API_URL}:get_missing_skills",
                kwargs={
                    "character_id": self.other_main.character_id,
                    "pk": self.combat.pk,
                },
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_doctrine_skills_should_return_skill_list(self):
        response = self.client.get(
            reverse(f"{API_URL}:get_doctrine_skills", kwargs={"pk": self.combat.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.json(),
            {
                "id": self.combat.pk,
                "name": "Combat",
                "category": "PvP",
                "ordering": 2,
                "active": True,
                "skills": {self.eve_type.name: 2, "Gunnery": 1},
                "character_skills": None,
            },
        )

    def test_doctrine_skills_should_add_skills_of_visible_character(self):
        response = self.client.get(
            reverse(f"{API_URL}:get_doctrine_skills", kwargs={"pk": self.combat.pk}),
            {"character_id": self.alt.character_id},
        )
        self.assertEqual(response.json()["character_skills"], {self.eve_type.name: 5})

    def test_doctrine_skills_should_hide_skills_of_foreign_character(self):
        response = self.client.get(
            reverse(f"{API_URL}:get_doctrine_skills", kwargs={"pk": self.combat.pk}),
            {"character_id": self.other_main.character_id},
        )
        self.assertIsNone(response.json()["character_skills"])

    def test_doctrine_skills_should_return_404_for_unknown_skill_list(self):
        response = self.client.get(
            reverse(f"{API_URL}:get_doctrine_skills", kwargs={"pk": 9999})
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
