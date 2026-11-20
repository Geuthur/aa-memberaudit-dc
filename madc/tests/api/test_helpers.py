"""TestAPI class."""

# Standard Library
import json
from http import HTTPStatus

# Third Party
# AA EVE SDE Factory
from evesde_factory.allianceauth import UserFactory

# Django
from django.urls import reverse

# Alliance Auth (External Libs)
from eveuniverse.models import EveType

# AA Memberaudit Doctrine Checker
from madc.api import helpers
from madc.models.skillchecker import SkillList
from madc.tests import AuthTestCase
from madc.tests.testdata.app import UserMainFactory
from madc.tests.testdata.load_eveuniverse import load_eveuniverse

API_PATH = "madc.api.admin"
API_URL = "madc:api"


class TestAPIHelper(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_eveuniverse()

        cls.user_admin_access = UserMainFactory(
            permissions__=[
                "madc.basic_access",
                "madc.corp_access",
                "madc.admin_access",
            ]
        )
        cls.user_no_access = UserMainFactory(permissions__=[])

        cls.eve_type = EveType.objects.get(id=17940)
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
            request, self.user_admin_access.profile.main_character.character_id
        )

        # then
        self.assertTrue(perms)
        self.assertEqual(
            main_char.character_id,
            self.user_admin_access.profile.main_character.character_id,
        )

    def test_get_main_character_should_not_load_all_visible_characters(self):
        # given: an admin sees every character
        request = self.factory.get("/")
        request.user = self.user_admin_access
        character_id = self.user.profile.main_character.character_id
        # when/then: one query for the character, one for the access check
        with self.assertNumQueries(2):
            perms, __ = helpers.get_main_character(request, character_id)
        self.assertTrue(perms)

    def test_get_main_character_no_access(self):
        # given
        request = self.factory.get("/")
        request.user = self.user_no_access

        # when
        perms, main_char = helpers.get_main_character(
            request, self.user_admin_access.profile.main_character.character_id
        )

        # then
        self.assertFalse(perms)
        self.assertEqual(
            main_char.character_id,
            self.user_admin_access.profile.main_character.character_id,
        )

    def test_get_main_character_should_deny_user_without_main_character(self):
        # given
        request = self.factory.get("/")
        request.user = UserFactory(permissions__=["madc.basic_access"])

        # when
        perms, main_char = helpers.get_main_character(
            request, self.user.profile.main_character.character_id
        )

        # then
        self.assertFalse(perms)
        self.assertEqual(main_char, self.user.profile.main_character)

    def test_get_corporation(self):
        # given
        request = self.factory.get("/")
        request.user = self.user_admin_access
        corporation_id = self.user.profile.main_character.corporation_id

        # when
        perms, corporation = helpers.get_corporation(request, corporation_id)

        # then
        self.assertTrue(perms)
        self.assertEqual(corporation.corporation_id, corporation_id)

    def test_get_corporation_no_access(self):
        # given
        request = self.factory.get("/")
        request.user = self.user_no_access
        corporation_id = self.user.profile.main_character.corporation_id

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
        alts_qs = helpers.get_alts_queryset(self.user.profile.main_character)

        # then
        self.assertIn(self.user.profile.main_character, alts_qs)
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
