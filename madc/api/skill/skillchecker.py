# Standard Library
from typing import Any

# Third Party
from ninja import NinjaAPI

# Django
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from memberaudit.models import Character

# AA Memberaudit Doctrine Checker
from madc import __title__, providers
from madc.api import schema
from madc.api.helpers import (
    _collect_user_doctrines,
    get_alts_queryset,
    get_corporation,
    get_main_character,
)
from madc.models import SkillList

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


class DoctrineCheckerApiEndpoints:
    tags = ["Doctrine Checker"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "{character_id}/doctrines/",
            response={200: list[schema.CharacterDoctrines], 403: str},
            tags=self.tags,
        )
        def get_doctrines(request, character_id: int):
            if character_id == 0:
                character_id = request.user.profile.main_character.character_id
            response, main = get_main_character(request, character_id)

            if not response:
                return 403, str(_("Permission Denied"))

            characters = get_alts_queryset(main)

            # Get the skill lists for the main character
            skilllists = providers.skills.get_user_skill_list(
                user_id=main.character_ownership.user_id
            )

            # Active skill lists are the ones that are visible in the UI
            visibles = list(
                SkillList.objects.filter(active=1).values_list("name", flat=True)
            )

            output = {}

            for c in characters:
                output[c.character_id] = {
                    "character": c,
                    "doctrines": {},
                    "skills": {},
                }

            for k, s in skilllists["skills_list"].items():
                for k, d in s["doctrines"].items():
                    # filter out hidden items
                    if k in visibles:
                        output[s["character_id"]]["doctrines"][k] = d
                # Add skills to the character
                output[s["character_id"]]["skills"] = s["skills"]

            return list(output.values())

        @api.get(
            "{corporation_id}/doctrines/view/corporation/",
            response={200: list[schema.CorporationDoctrines], 403: str},
            tags=self.tags,
        )
        def get_corporation_doctrines(request, corporation_id: int):
            if corporation_id == 0:
                corporation_id = request.user.profile.main_character.corporation_id
            perm, __ = get_corporation(request, corporation_id)

            if not perm:
                return 403, str(_("Permission Denied"))

            # Get all characters in the corporation
            corporation_characters = Character.objects.filter(
                eve_character__corporation_id=corporation_id,
            ).select_related(
                "eve_character",
                "eve_character__character_ownership",
                "eve_character__character_ownership__user",
            )

            # Active skill lists are the ones that are visible in the UI
            active_skilllists = list(
                SkillList.objects.filter(active=1).values_list("name", flat=True)
            )

            # Process corporation members and build character data
            users, main_characters, all_characters = self._process_corporation_members(
                corporation_characters
            )

            # Get skill lists for all users
            skilllists = providers.skills.get_users_skill_list(users)

            # Process skill data for each user
            self._process_user_skills(
                skilllists, main_characters, all_characters, active_skilllists
            )

            return list(main_characters.values())

        @api.get(
            "{character_id}/doctrines/{pk}/",
            response={200: Any, 403: str},
            tags=self.tags,
        )
        def get_missing_skills(request, character_id: int, pk: int):
            if character_id == 0:
                character_id = request.user.profile.main_character.character_id
            response, character = get_main_character(request, character_id)

            if not response:
                return 403, str(_("Permission Denied"))

            # Get the skill lists for the main character
            user_skilllists = providers.skills.get_user_skill_list(
                user_id=character.character_ownership.user_id
            )

            try:
                skilllist = SkillList.objects.get(pk=pk)
            except SkillList.DoesNotExist:
                return render(
                    request,
                    "madc/partials/modals/missing.html",
                )

            doctrine_skills = skilllist.get_skills()

            # Find the character in the skill lists
            character_skills = self._find_character_skills(
                user_skilllists["skills_list"], character_id
            )

            if character_skills is None:
                return 403, _("Character not found in skill lists")

            # Compare required skills with character skills
            missing_skills = self._compare_skills(doctrine_skills, character_skills)

            context = {"doctrine": skilllist, "skills": missing_skills}

            return render(request, "madc/partials/modals/missing.html", context=context)

        @api.get(
            "doctrines/{pk}/",
            response={200: Any, 403: str},
            tags=self.tags,
        )
        def get_doctrine_skills(request, pk: int):
            perms = request.user.has_perm("madc.basic_access")

            if not perms:
                return 403, str(_("Permission Denied"))

            try:
                skilllist = SkillList.objects.get(pk=pk)
            except SkillList.DoesNotExist:
                return render(
                    request,
                    "madc/partials/modals/missing.html",
                )

            context = {"doctrine": skilllist}

            return render(
                request, "madc/partials/modals/doctrine.html", context=context
            )

    def _create_character_data(self, character: Character) -> dict[str, Any]:
        """Helper function to create character data."""
        return {
            "character_name": character.character_name,
            "character_id": character.character_id,
            "corporation_id": character.corporation_id,
            "corporation_name": character.corporation_name,
            "alliance_id": character.alliance_id,
            "alliance_name": character.alliance_name,
        }

    def _process_corporation_members(self, corporation_characters: list[Character]):
        """Process corporation members and build character data structures."""
        users = set()
        main_characters = {}
        all_characters = {}

        # Create a dictionary to hold all characters
        for member in corporation_characters:
            # Store all character data for later use
            all_characters[member.eve_character.character_id] = (
                self._create_character_data(member.eve_character)
            )

            # Process users with main characters
            if (
                member.user
                and hasattr(member.user, "profile")
                and member.user.profile.main_character
            ):
                users.add(member.user)
                main_char = member.user.profile.main_character

                # Only add if we haven't processed this main character yet
                if main_char.character_id not in main_characters:
                    main_characters[main_char.character_id] = {
                        "user_id": member.user.id,
                        "character": self._create_character_data(main_char),
                        "alts": [],
                        "doctrines": {},
                    }

        return users, main_characters, all_characters

    def _process_user_skills(
        self, skilllists, main_characters, all_characters, active_skilllists
    ):
        """Process skill data for each user."""
        corp_character_ids = set(all_characters.keys())

        for user_id, corp_data in skilllists.items():
            if not ("data" in corp_data and "skills_list" in corp_data["data"]):
                continue

            # Filter to corporation characters only
            corp_skills_list = {
                char_key: char_data
                for char_key, char_data in corp_data["data"]["skills_list"].items()
                if char_data["character_id"] in corp_character_ids
            }

            if not corp_skills_list:
                continue

            # Find the main character for this user
            main_char_id = self._find_main_character_id(main_characters, user_id)

            if main_char_id and main_char_id in main_characters:
                # Collect doctrines
                user_doctrines = _collect_user_doctrines(
                    corp_skills_list, active_skilllists
                )
                main_characters[main_char_id]["doctrines"] = user_doctrines

                # Collect alts (all corp characters except main)
                alts = [
                    all_characters[char_data["character_id"]]
                    for char_data in corp_skills_list.values()
                    if char_data["character_id"] != main_char_id
                ]
                main_characters[main_char_id]["alts"] = alts

    def _find_main_character_id(self, main_characters, user_id):
        """Find the main character ID for a given user ID."""
        for char_id, char_data in main_characters.items():
            if char_data["user_id"] == user_id:
                return char_id
        return None

    def _find_character_skills(self, skills_list: dict, character_id: int) -> dict:
        """Find character skills in the skills list."""
        for character_data in skills_list.values():
            if character_data["character_id"] == character_id:
                return character_data["skills"]
        return None

    def _compare_skills(self, doctrine_skills: dict, character_skills: dict) -> list:
        """Compare required skills with character skills."""
        missing_skills = []
        for skill_name, required_level in doctrine_skills.items():
            trained_level = 0
            if skill_name in character_skills:
                trained_level = character_skills[skill_name].get("trained_level", 0)

            missing_skills.append(
                {
                    "skill": skill_name,
                    "trained": trained_level,
                    "needed": required_level,
                }
            )
        return missing_skills
