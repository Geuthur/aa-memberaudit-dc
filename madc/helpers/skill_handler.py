# Standard Library
import json
from hashlib import md5

# Django
from django.apps import apps
from django.contrib.auth.models import User
from django.core.cache import cache
from django.urls import reverse
from django.utils.html import format_html

# Alliance Auth
from allianceauth.authentication.models import CharacterOwnership
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


def fittings_installed() -> bool:
    return apps.is_installed(app_name="fittings")


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

    def _generate_doctrine_html(
        self,
        skill_list_name: str,
        character_id: int,
        has_missing_skills: bool,
        skill_list_pk: int = None,
    ) -> str:
        """Generate HTML for doctrine buttons based on skill status."""
        html = f"<div class='doctrine-item btn-group' role='group' data-doctrine='{skill_list_name}'>"
        html += "<button type='button' "

        if has_missing_skills:
            url = reverse(
                viewname="madc:api:get_missing_skills",
                kwargs={"character_id": character_id, "pk": skill_list_pk},
            )
            html += f"class='btn btn-danger btn-sm' id='missing-{skill_list_name}-{character_id}' data-bs-toggle='modal' data-bs-target='#modalViewMissingContainer' data-ajax_missing='{url}'>"
        else:
            html += "class='btn btn-success btn-sm'>"

        html += f"{skill_list_name}</button>"
        html += "<button type='button' class='flex-one btn "

        if has_missing_skills:
            html += f"btn-danger btn-sm' id='copy-{skill_list_name}-{character_id}'>"
            html += "<i class='fa-solid fa-copy'></i>"
        else:
            html += "btn-success btn-sm'>"
            html += "<i class='fa-solid fa-check'></i>"
        html += "</button></div>"

        return format_html(html)

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
                character_data["doctrines"][skill_list_name]["order"] = skill_list_misc[
                    skill_list_name
                ]["order-weight"]
                character_data["doctrines"][skill_list_name]["category"] = (
                    skill_list_misc[skill_list_name]["category"]
                )

                has_missing_skills = bool(
                    character_data["doctrines"][skill_list_name]["skills"]
                )
                character_data["doctrines"][skill_list_name]["html"] = (
                    self._generate_doctrine_html(
                        skill_list_name=skill_list_name,
                        character_id=character_data["character_id"],
                        has_missing_skills=has_missing_skills,
                        skill_list_pk=skill_list_misc[skill_list_name]["pk"],
                    )
                )
        return skill_dict

    def get_users_skill_list(self, users):
        """Get the skill list for multiple users."""
        linked_characters = CharacterOwnership.objects.filter(user__in=users).values(
            "user_id", "character__character_name", "character__character_id"
        )

        skill_lists = SkillList.objects.all().order_by("ordering", "name")
        skill_list_hash = self._get_skill_list_hash(skill_lists.values_list("name"))
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
        skill_list_hash = self._get_skill_list_hash(skill_lists.values_list("name"))
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
