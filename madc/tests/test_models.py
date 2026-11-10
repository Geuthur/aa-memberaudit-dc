# Standard Library
import json

# AA Memberaudit Doctrine Checker
from madc import __title__
from madc.models.skillchecker import SkillList, skillvalidator
from madc.tests import NoSocketsTestCase
from madc.tests.testdata.load_eveuniverse import load_eveuniverse


class TestModelsSkillChecker(NoSocketsTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_eveuniverse()

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
