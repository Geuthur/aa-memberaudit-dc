# Standard Library
import json
from hashlib import md5

# Django
from django.contrib.auth.models import User
from django.core.cache import cache

# Alliance Auth
from allianceauth.authentication.models import CharacterOwnership

# Alliance Auth (External Libs)
from memberaudit.models import CharacterSkill

# AA Memberaudit Doctrine Checker
from madc.models.skillchecker import SkillList
from madc.providers import logger

SKILL_CACHE_TIMEOUT_SECONDS = 60 * 60 * 72  # 72 hours
# Keys with a version: a new version drops results cached in an older format
SKILL_CACHE_HEADERS_KEY = "SKILL_HEADER_V3"
SKILL_CACHE_USER_KEY = "SKILL_LISTS_V3_{}"


class SkillListHandler:
    """handler for skill lists."""

    def _get_skill_list_hash(self, skill_lists) -> str:
        """
        Generate a hash over everything of the skill lists that changes a result.

        Name, category, ordering, active flag and the skills are part of the
        cached check results, so a change of any of them gives a new hash.
        """
        rows = sorted(
            skill_lists.values_list(
                "pk", "name", "category", "ordering", "active", "skill_list"
            )
        )
        return md5(json.dumps(rows).encode()).hexdigest()

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
        skill_list_misc = {}

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
            skill_list_misc[skill_list.name] = {}
            skill_list_misc[skill_list.name]["pk"] = skill_list.pk
            skill_list_misc[skill_list.name]["order-weight"] = skill_list.ordering
            skill_list_misc[skill_list.name]["category"] = skill_list.category

        for character, character_data in skill_dict.items():
            character_data["doctrines"] = {}
            for skill_list_name, skills in skill_list_dict.items():
                character_data["doctrines"][skill_list_name] = {}
                character_data["doctrines"][skill_list_name]["skills"] = {}
                for skill, level in skills.items():
                    level = int(level)
                    if level > character_data["skills"].get(skill, {}).get(
                        "active_level", 0
                    ):
                        character_data["doctrines"][skill_list_name]["skills"][
                            skill
                        ] = level

                # Add metadata for the doctrine
                character_data["doctrines"][skill_list_name]["id"] = skill_list_misc[
                    skill_list_name
                ]["pk"]
                character_data["doctrines"][skill_list_name]["order"] = skill_list_misc[
                    skill_list_name
                ]["order-weight"]
                character_data["doctrines"][skill_list_name]["category"] = (
                    skill_list_misc[skill_list_name]["category"]
                )
        return skill_dict

    def get_users_skill_list(self, users):
        """Get the skill list for multiple users."""
        linked_characters = CharacterOwnership.objects.filter(user__in=users).values(
            "user_id", "character__character_name", "character__character_id"
        )

        skill_lists = SkillList.objects.all().order_by("ordering", "name")
        skill_list_hash = self._get_skill_list_hash(skill_lists)
        cached_header = cache.get(SKILL_CACHE_HEADERS_KEY, False)
        skill_lists_up_to_date = cached_header == skill_list_hash

        user_chars = {}
        for u in linked_characters:
            if u["user_id"] not in user_chars:
                user_chars[u["user_id"]] = {"chars": []}
            user_chars[u["user_id"]]["chars"].append(u["character__character_id"])

        for uid, c in user_chars.items():
            if skill_lists_up_to_date:
                cache_key = self._build_account_cache_key(c["chars"])
                cached_skills = cache.get(cache_key, False)

                if cached_skills is not False:  # check if cached at all?
                    cached_skills = json.loads(cached_skills)
                    if cached_skills.get("doctrines", False) != skill_list_hash:
                        c["data"] = self.get_user_skill_list(uid)
                    else:
                        c["data"] = cached_skills
                else:
                    c["data"] = self.get_user_skill_list(uid)
            else:
                c["data"] = self.get_user_skill_list(uid)

        return user_chars

    def get_user_skill_list(self, user_id: int, force_rebuild=True) -> dict:
        """Get the skill list for a user."""
        linked_characters = (
            User.objects.get(id=user_id)
            .character_ownerships.all()
            .values_list("character__character_id", flat=True)
        )

        skill_lists = SkillList.objects.all().order_by("ordering", "name")
        skill_list_hash = self._get_skill_list_hash(skill_lists)
        cached_header = cache.get(SKILL_CACHE_HEADERS_KEY, False)
        skill_lists_up_to_date = cached_header == skill_list_hash

        account_key = self._build_account_cache_key(linked_characters)

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


skill_list_handler = SkillListHandler()
