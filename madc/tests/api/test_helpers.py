"""TestAPI class."""

# Standard Library
import json
from http import HTTPStatus

# Django
from django.test import RequestFactory, TestCase
from django.urls import reverse

# Alliance Auth (External Libs)
from app_utils.testing import create_user_from_evecharacter
from eveuniverse.models import EveType
from memberaudit.models import Character

# AA Memberaudit Doctrine Checker
from madc.api import helpers
from madc.models.skillchecker import SkillList
from madc.tests.testdata.load_allianceauth import load_allianceauth
from madc.tests.testdata.load_eveuniverse import load_eveuniverse
from madc.tests.testdata.load_memberaudit import load_memberaudit

API_PATH = "madc.api.admin"
API_URL = "madc:api"


class TestAPIHelper(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_eveuniverse()
        load_memberaudit()

        cls.factory = RequestFactory()
        cls.user_no_access, cls.character_ownership_no_access = (
            create_user_from_evecharacter(
                character_id=1000,
                permissions=[],
            )
        )
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

        cls.eve_type = EveType.objects.get(id=17940)
        cls.memberaudit = Character.objects.get(eve_character__character_id=1001)
        cls.skill_list = SkillList.objects.create(
            name="Test Skill Ready",
            category="Test Category",
            active=True,
            skill_list=json.dumps({str(cls.eve_type.name): 5}),
            ordering=1,
        )
        cls.skill_list2 = SkillList.objects.create(
            name="Test Skill Baby",
            active=True,
            skill_list=json.dumps({str(cls.eve_type.name): 5}),
            ordering=1,
        )

    def test_get_main_character(self):
        # given
        request = self.factory.get("/")
        request.user = self.user_admin_access

        # when
        perms, main_char = helpers.get_main_character(
            request, self.character_ownership_admin.character.character_id
        )

        # then
        self.assertTrue(perms)
        self.assertEqual(
            main_char.character_id,
            self.character_ownership_admin.character.character_id,
        )

    def test_get_main_character_no_access(self):
        # given
        request = self.factory.get("/")
        request.user = self.user_no_access

        # when
        perms, main_char = helpers.get_main_character(
            request, self.character_ownership_admin.character.character_id
        )

        # then
        self.assertFalse(perms)
        self.assertEqual(
            main_char.character_id,
            self.character_ownership_admin.character.character_id,
        )

    def test_get_corporation(self):
        # given
        request = self.factory.get("/")
        request.user = self.user_admin_access
        corporation_id = self.character_ownership.character.corporation_id

        # when
        perms, corporation = helpers.get_corporation(request, corporation_id)

        # then
        self.assertTrue(perms)
        self.assertEqual(corporation.corporation_id, corporation_id)

    def test_get_corporation_no_access(self):
        # given
        request = self.factory.get("/")
        request.user = self.user_no_access
        corporation_id = self.character_ownership.character.corporation_id

        # when
        perms, corporation = helpers.get_corporation(request, corporation_id)

        # then
        self.assertFalse(perms)
        self.assertEqual(corporation.corporation_id, corporation_id)

    def test_get_corporation_not_exist(self):
        # given
        request = self.factory.get("/")
        request.user = self.user_admin_access
        corporation_id = 99999999  # Non-existent corporation ID

        # when
        perms, corporation = helpers.get_corporation(request, corporation_id)

        # then
        self.assertFalse(perms)
        self.assertIsNone(corporation)

    def test_get_alts_queryset(self):
        # when
        alts_qs = helpers.get_alts_queryset(self.character_ownership.character)

        # then
        self.assertIn(self.character_ownership.character, alts_qs)
        self.assertEqual(alts_qs.count(), 1)

    def test__collect_user_doctrines_single_char(self):
        # given
        request = self.factory.get("/")
        request.user = self.user_admin_access

        skills_list = {
            "Gneuten": {
                "character_id": 1001,
                "skills": {
                    "Acceleration Control": {
                        "skill_group": "Navigation",
                        "sp_total": 1024000,
                        "active_level": 5,
                        "trained_level": 5,
                    },
                    "XL Torpedoes": {
                        "skill_group": "Missiles",
                        "sp_total": 1792000,
                        "active_level": 5,
                        "trained_level": 5,
                    },
                    "Heavy Fighters": {
                        "skill_group": "Fighters",
                        "sp_total": 819200,
                        "active_level": 5,
                        "trained_level": 5,
                    },
                },
                "doctrines": {
                    "Test Skill Ready": {
                        "skills": {},
                        "order": 0,
                        "category": "SIGMA",
                        "html": "<div class='doctrine-item btn-group' role='group' data-doctrine='Test Skill Ready'><button type='button' class='btn btn-success btn-sm'>Test Skill Ready</button><button type='button' class='flex-one btn btn-success btn-sm'><i class='fa-solid fa-check'></i></button></div>",
                    },
                },
            },
        }

        active_skilllists = [str(self.skill_list.name), str(self.skill_list2.name)]

        # when
        doctrines = helpers._collect_user_doctrines(
            skills_list=skills_list, active_skilllists=active_skilllists
        )
        # then
        self.assertIn("Test Skill Ready", doctrines)

    def test__collect_user_doctrines_multiple_chars(self):
        # given
        request = self.factory.get("/")
        request.user = self.user_admin_access

        skills_list = {
            "Gneuten": {
                "character_id": 1001,
                "skills": {
                    "Acceleration Control": {
                        "skill_group": "Navigation",
                        "sp_total": 1024000,
                        "active_level": 5,
                        "trained_level": 5,
                    },
                    "XL Torpedoes": {
                        "skill_group": "Missiles",
                        "sp_total": 1792000,
                        "active_level": 5,
                        "trained_level": 5,
                    },
                    "Heavy Fighters": {
                        "skill_group": "Fighters",
                        "sp_total": 819200,
                        "active_level": 5,
                        "trained_level": 5,
                    },
                },
                "doctrines": {
                    "Test Skill Ready": {
                        "skills": {},
                        "order": 0,
                        "category": "SIGMA",
                        "html": "<div class='doctrine-item btn-group' role='group' data-doctrine='Test Skill Ready'><button type='button' class='btn btn-success btn-sm'>Test Skill Ready</button><button type='button' class='flex-one btn btn-success btn-sm'><i class='fa-solid fa-check'></i></button></div>",
                    },
                },
            },
            "rotze Rotineque": {
                "character_id": 1002,
                "skills": {
                    "Acceleration Control": {
                        "skill_group": "Navigation",
                        "sp_total": 1792000,
                        "active_level": 2,
                        "trained_level": 3,
                    },
                    "XL Torpedoes": {
                        "skill_group": "Missiles",
                        "sp_total": 1092000,
                        "active_level": 3,
                        "trained_level": 4,
                    },
                },
                "doctrines": {
                    "Test Skill Ready": {
                        "skills": {"XL Torpedoes": 5, "Heavy Fighters": 5},
                        "order": 0,
                        "category": "SIGMA",
                        "html": "<div class='doctrine-item btn-group' role='group' data-doctrine='Test Skill Ready'><button type='button' class='btn btn-success btn-sm'>Test Skill Ready</button><button type='button' class='flex-one btn btn-success btn-sm'><i class='fa-solid fa-check'></i></button></div>",
                    },
                },
            },
            "Hector Fieramosca": {
                "character_id": 1003,
                "skills": {},
                "doctrines": {
                    "Test Skill Ready": {
                        "skills": {"XL Torpedoes": 5, "Heavy Fighters": 5},
                        "order": 0,
                        "category": "SIGMA",
                        "html": "<div class='doctrine-item btn-group' role='group' data-doctrine='Test Skill Ready'><button type='button' class='btn btn-success btn-sm'>Test Skill Ready</button><button type='button' class='flex-one btn btn-success btn-sm'><i class='fa-solid fa-check'></i></button></div>",
                    },
                },
            },
        }

        active_skilllists = [str(self.skill_list.name), str(self.skill_list2.name)]

        # when
        doctrines = helpers._collect_user_doctrines(
            skills_list=skills_list, active_skilllists=active_skilllists
        )
        # then
        self.assertIn("Test Skill Ready", doctrines)
        self.assertNotIn("XL Torpedoes", doctrines["Test Skill Ready"]["skills"])

    def test__collect_user_doctrines_multiple_chars_missing_skills(self):
        # given
        request = self.factory.get("/")
        request.user = self.user_admin_access

        skills_list = {
            "rotze Rotineque": {
                "character_id": 1002,
                "skills": {
                    "Acceleration Control": {
                        "skill_group": "Navigation",
                        "sp_total": 1792000,
                        "active_level": 2,
                        "trained_level": 3,
                    },
                    "XL Torpedoes": {
                        "skill_group": "Missiles",
                        "sp_total": 1092000,
                        "active_level": 3,
                        "trained_level": 4,
                    },
                },
                "doctrines": {
                    "Test Skill Ready": {
                        "skills": {"XL Torpedoes": 5, "Heavy Fighters": 5},
                        "order": 0,
                        "category": "SIGMA",
                        "html": "<div class='doctrine-item btn-group' role='group' data-doctrine='Test Skill Ready'><button type='button' class='btn btn-success btn-sm'>Test Skill Ready</button><button type='button' class='flex-one btn btn-success btn-sm'><i class='fa-solid fa-check'></i></button></div>",
                    },
                },
            },
            "Hector Fieramosca": {
                "character_id": 1003,
                "skills": {},
                "doctrines": {
                    "Test Skill Ready": {
                        "skills": {"XL Torpedoes": 5, "Heavy Fighters": 5},
                        "order": 0,
                        "category": "SIGMA",
                        "html": "<div class='doctrine-item btn-group' role='group' data-doctrine='Test Skill Ready'><button type='button' class='btn btn-success btn-sm'>Test Skill Ready</button><button type='button' class='flex-one btn btn-success btn-sm'><i class='fa-solid fa-check'></i></button></div>",
                    },
                },
            },
        }

        active_skilllists = [str(self.skill_list.name), str(self.skill_list2.name)]

        # when
        doctrines = helpers._collect_user_doctrines(
            skills_list=skills_list, active_skilllists=active_skilllists
        )
        # then
        self.assertIn("Test Skill Ready", doctrines)
        self.assertIn("XL Torpedoes", doctrines["Test Skill Ready"]["skills"])

    def test__collect_user_doctrines_no_active_skilllists(self):
        # given
        request = self.factory.get("/")
        request.user = self.user_admin_access

        skills_list = {
            "Gneuten": {
                "character_id": 1001,
                "skills": {
                    "Acceleration Control": {
                        "skill_group": "Navigation",
                        "sp_total": 1024000,
                        "active_level": 5,
                        "trained_level": 5,
                    },
                    "XL Torpedoes": {
                        "skill_group": "Missiles",
                        "sp_total": 1792000,
                        "active_level": 5,
                        "trained_level": 5,
                    },
                    "Heavy Fighters": {
                        "skill_group": "Fighters",
                        "sp_total": 819200,
                        "active_level": 5,
                        "trained_level": 5,
                    },
                },
                "doctrines": {
                    "Test Skill Ready": {
                        "skills": {},
                        "order": 0,
                        "category": "SIGMA",
                        "html": "<div class='doctrine-item btn-group' role='group' data-doctrine='Test Skill Ready'><button type='button' class='btn btn-success btn-sm'>Test Skill Ready</button><button type='button' class='flex-one btn btn-success btn-sm'><i class='fa-solid fa-check'></i></button></div>",
                    },
                },
            },
        }

        active_skilllists = []

        # when
        doctrines = helpers._collect_user_doctrines(
            skills_list=skills_list, active_skilllists=active_skilllists
        )
        # then
        self.assertEqual(doctrines, {})

    def test__collect_user_doctrines_no_doctrines(self):
        # given
        request = self.factory.get("/")
        request.user = self.user_admin_access

        skills_list = {
            "Gneuten": {
                "character_id": 1001,
                "skills": {
                    "Acceleration Control": {
                        "skill_group": "Navigation",
                        "sp_total": 1024000,
                        "active_level": 5,
                        "trained_level": 5,
                    },
                    "XL Torpedoes": {
                        "skill_group": "Missiles",
                        "sp_total": 1792000,
                        "active_level": 5,
                        "trained_level": 5,
                    },
                    "Heavy Fighters": {
                        "skill_group": "Fighters",
                        "sp_total": 819200,
                        "active_level": 5,
                        "trained_level": 5,
                    },
                },
            },
        }

        active_skilllists = [str(self.skill_list.name), str(self.skill_list2.name)]

        # when
        doctrines = helpers._collect_user_doctrines(
            skills_list=skills_list, active_skilllists=active_skilllists
        )
        # then
        self.assertEqual(doctrines, {})
