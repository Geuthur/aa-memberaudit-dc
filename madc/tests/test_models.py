# Standard Library
import json

# Django
from django.test import RequestFactory

# Alliance Auth (External Libs)
from app_utils.testing import NoSocketsTestCase, create_user_from_evecharacter
from eveuniverse.models import EveType
from memberaudit.models import Character

# AA Memberaudit Doctrine Checker
from madc import __title__
from madc.models.skillchecker import SkillList, skillvalidator
from madc.tests.testdata.load_allianceauth import load_allianceauth
from madc.tests.testdata.load_eveuniverse import load_eveuniverse
from madc.tests.testdata.load_memberaudit import load_memberaudit


class TestModelsSkillChecker(NoSocketsTestCase):
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

    def test__str__(self):
        """Test should return skill checker string representation."""
        skill_checker = SkillList(
            name="Test Skill Checker",
            skill_list=json.dumps({"Mining Barge": 3}),
        )
        self.assertEqual(
            str(skill_checker),
            f"{skill_checker.name} ({skill_checker.ordering})",
        )

    def test_skillvalidator_is_valid(self):
        """Test should validate skills correctly."""
        # given
        sk_check = {
            "Mining Barge": 3,
        }

        result = skillvalidator(value=json.dumps(sk_check))

        self.assertIsNone(result)

    def test_skillvalidator_invalid_skill(self):
        """Test should raise ValidationError for invalid skill."""
        # given
        sk_check = {
            "Invalid Skill": 3,
        }

        with self.assertRaisesMessage(Exception, "Invalid Skill is not a valid skill."):
            skillvalidator(value=json.dumps(sk_check))

    def test_skillvalidator_invalid_level(self):
        """Test should raise ValidationError for invalid skill level."""
        # given
        sk_check = {
            "Mining Barge": 10,
        }

        with self.assertRaisesMessage(
            Exception, "Mining Barge level must be between 0 and 5."
        ):
            skillvalidator(value=json.dumps(sk_check))

    def test_skillvalidator_non_integer_level(self):
        """Test should raise ValidationError for non-integer skill level."""
        # given
        sk_check = {
            "Mining Barge": "high",
        }

        with self.assertRaisesMessage(
            Exception, "Mining Barge level must be an integer."
        ):
            skillvalidator(value=json.dumps(sk_check))

    def test_skillvalidator_invalid_json(self):
        """Test should raise ValidationError for invalid JSON."""
        # given
        sk_check = "Not a JSON string"

        with self.assertRaisesMessage(
            Exception, "Please provide a valid skill list in JSON format."
        ):
            skillvalidator(value=sk_check)
