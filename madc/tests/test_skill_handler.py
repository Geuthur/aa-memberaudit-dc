# Standard Library
import json

# Alliance Auth (External Libs)
from eveuniverse.models import EveType
from memberaudit.models import CharacterSkill

# AA Memberaudit Doctrine Checker
from madc import __title__
from madc.helpers.skill_handler import SkillListHandler
from madc.models import SkillList
from madc.tests import AuthTestCase
from madc.tests.testdata.load_eveuniverse import load_eveuniverse
from madc.tests.testdata.load_memberaudit import create_memberaudit


class TestSkillHandler(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_eveuniverse()

        cls.eve_type = EveType.objects.get(id=17940)
        cls.memberaudit = create_memberaudit(cls.user.profile.main_character)

    def test_get_skill_list_hash(self):
        """Test should generate correct skill list hash."""
        # given
        handler = SkillListHandler()
        skills = ["Skill A", "Skill B", "Skill C"]
        expected_hash = "3d6a81fde9ea9a3e2e791536378c37f6"
        # then
        self.assertEqual(handler._get_skill_list_hash(skills), expected_hash)

    def test_get_chars_hash(self):
        """Test should generate correct character hash."""
        # given
        handler = SkillListHandler()
        characters = [1001, 1002, 1003]
        expected_hash = "fee1f06f37321e04f41a8caaa2f23330"
        # then
        self.assertEqual(handler._get_chars_hash(characters), expected_hash)

    def test_check_skill_lists(self):
        """Test should check skill lists for linked characters."""
        # given
        sk_check = {
            "Skill II": 2,
            "Skill I": 1,
        }

        skill_list = SkillList.objects.create(
            name="fit", skill_list=json.dumps(sk_check)
        )

        CharacterSkill.objects.create(
            character=self.memberaudit,
            eve_type=self.eve_type,
            active_skill_level=3,
            skillpoints_in_skill=900000,
            trained_skill_level=5,
        )

        handler = SkillListHandler()
        linked_characters = [self.user.profile.main_character.character_id]
        # when
        result = handler.check_skill_lists(
            skill_lists=[skill_list],
            linked_characters=linked_characters,
        )

        character_name = self.memberaudit.eve_character.character_name
        # then
        self.assertIn(character_name, result)
        self.assertIn("fit", result[character_name]["doctrines"])
        self.assertEqual(
            result[character_name]["doctrines"]["fit"]["id"], skill_list.pk
        )
        self.assertIn("Mining Barge", result[character_name]["skills"])

    def test_check_skill_lists_no_skills(self):
        """Test should check skill lists for linked characters with no skills."""
        # given
        sk_check = {
            "Skill II": 2,
            "Skill I": 1,
        }

        skill_list = SkillList(name="fit", skill_list=json.dumps(sk_check))

        handler = SkillListHandler()
        linked_characters = [self.user.profile.main_character.character_id]
        # when
        result = handler.check_skill_lists(
            skill_lists=[skill_list],
            linked_characters=linked_characters,
        )
        # then
        self.assertEqual({}, result)

    def test_get_users_skill_lists(self):
        """Test should get users skill lists."""
        # given
        handler = SkillListHandler()
        # when
        result = handler.get_users_skill_list([self.user])
        # then
        self.assertIn(self.user.pk, result)
        self.assertIn(
            self.memberaudit.eve_character.character_id, result[self.user.pk]["chars"]
        )
        self.assertIn("doctrines", result[self.user.pk]["data"])
        self.assertIn("characters", result[self.user.pk]["data"])
        self.assertIn("skills_list", result[self.user.pk]["data"])
