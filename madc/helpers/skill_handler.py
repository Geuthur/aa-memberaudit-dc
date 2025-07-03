# Standard Library
import json
from hashlib import md5

# Django
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.html import format_html

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from memberaudit.models import CharacterSkill

# AA Memberaudit Doctrine Checker
from madc import __title__
from madc.models.skillchecker import SkillList

SKILL_CACHE_TIMEOUT_SECONDS = 60 * 60 * 72  # 72 hours
SKILL_CACHE_HEADERS_KEY = "SKILL_HEADER"
SKILL_CACHE_USER_KEY = "SKILL_LISTS_{}"

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


class SkillListHandler:
    """handler for skill lists."""

    def _get_skill_list_hash(self, skills: list[str]) -> str:
        """Generate a hash for the skill list names."""
        return md5(",".join(str(x) for x in sorted(skills)).encode()).hexdigest()

    def _get_chars_hash(self, characters: list[int]) -> str:
        return md5(",".join(str(x) for x in sorted(characters)).encode()).hexdigest()

    def _build_account_cache_key(self, characters):
        """Build a cache key based on the character IDs."""
        return SKILL_CACHE_USER_KEY.format(self._get_chars_hash(characters))

    def check_skill_lists(self, skill_lists: list[SkillList], linked_characters):
        """Check if the skill lists are up to date."""

        skills = (
            CharacterSkill.objects.filter(
                character__eve_character__character_id__in=linked_characters
            )
            .select_related(
                "eve_type", "eve_type__eve_group", "character__eve_character"
            )
            .order_by("eve_type__name")
        )

        skill_dict = {}
        skill_list_dict = {}

        for skill in skills:
            character = skill.character.eve_character.character_name
            skill_group = skill.eve_type.eve_group.name

            # Create a new entry for the character if it doesn't exist
            if character not in skill_dict:
                skill_dict[character] = {
                    "character_id": skill.character.eve_character.character_id,
                    "skills": {},
                }

            # Add the skill to the dictionary
            skill_dict[character]["skills"][skill.eve_type.name] = {
                "skill_group": skill_group,
                "sp_total": skill.skillpoints_in_skill,
                "active_level": skill.active_skill_level,
                "trained_level": skill.trained_skill_level,
            }

        # Get the skill lists and their skills
        for skill_list in skill_lists:
            skill_list_dict[skill_list.name] = skill_list.get_skills()

        for character, character_data in skill_dict.items():
            character_data["doctrines"] = {}
            for skill_list_name, skills in skill_list_dict.items():
                character_data["doctrines"][skill_list_name] = {}
                for skill, level in skills.items():
                    level = int(level)
                    if level > character_data["skills"].get(skill, {}).get(
                        "active_level", 0
                    ):
                        character_data["doctrines"][skill_list_name][skill] = level

                # TODO: Make a Helper to Handle HTML Formatting
                # Add Modal Overview for missing skills for each Character
                # Add HTML to each individual doctrine
                if character_data["doctrines"][skill_list_name]:
                    character_data["doctrines"][skill_list_name]["html"] = format_html(
                        """
                            <div role="group" class="btn-group">
                                <button type="button" class="btn btn-danger btn-sm" id="missing-{}-{}" data->
                                    {}
                                </button>
                                <button type="button" class="flex-one btn btn-danger btn-sm" id="copy-{}-{}">
                                    <i class="fa-solid fa-copy"></i>
                                </button>
                            </div>
                        """,
                        skill_list_name,
                        character_data["character_id"],
                        md5(skill_list_name.encode()).hexdigest(),
                    )
                else:
                    character_data["doctrines"][skill_list_name]["html"] = format_html(
                        """
                            <div role="group" class="btn-group">
                                <button type="button" class="btn btn-success btn-sm">
                                    {}
                                </button>
                                <button type="button" class="flex-one btn btn-success btn-sm">
                                    <i class="fa-solid fa-check"></i>
                                </button>
                            </div>
                        """,
                        skill_list_name,
                    )
        return skill_dict

    def get_user_skill_list(self, user_id: int, force_rebuild=False) -> dict:
        """Get the skill list for a user."""
        linked_characters = (
            User.objects.get(id=user_id)
            .character_ownerships.all()
            .values_list("character__character_id", flat=True)
        )
        skill_lists = SkillList.objects.all().order_by("ordering", "name")
        skill_list_hash = self._get_skill_list_hash(skill_lists.values_list("name"))
        account_key = self._build_account_cache_key(linked_characters)
        cached_header = cache.get(SKILL_CACHE_HEADERS_KEY, False)
        skill_lists_up_to_date = cached_header == skill_list_hash

        if skill_lists_up_to_date and not force_rebuild:
            cached_skills = cache.get(account_key, False)

            if cached_skills is not False:
                logger.debug(
                    "Using cached skill list for user %s: %s",
                    user_id,
                    account_key,
                )
                cached_skills = json.loads(cached_skills)
                if cached_skills.get("doctrines", False) == skill_list_hash:
                    return cached_skills

        output = {
            "doctrines": skill_list_hash,
            "characters": account_key,
            "skills_list": self.check_skill_lists(skill_lists, linked_characters),
        }
        
        output_json = json.dumps(output)

        cache.set(
            account_key,
            output_json,
            SKILL_CACHE_TIMEOUT_SECONDS,
        )
        cache.set(SKILL_CACHE_HEADERS_KEY, skill_list_hash)
        return output
