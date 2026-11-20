"""Doctrine API endpoints: skill check of accounts and corporations."""

# Standard Library
from collections import defaultdict
from http import HTTPStatus
from typing import Any

# Third Party
from ninja import NinjaAPI, Query

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from memberaudit.models import Character, CharacterSkill

# AA Memberaudit Doctrine Checker
from madc.api import schema
from madc.api.helpers import (
    _collect_user_doctrines,
    get_alts_queryset,
    get_corporation,
    get_main_character,
    get_skill_list,
    skill_list_fields,
)
from madc.helpers.skill_handler import skill_list_handler
from madc.models import SkillList


def _character_schema(character: EveCharacter | dict) -> schema.CharacterSchema:
    """Build a CharacterSchema from an EveCharacter or its data dict."""
    if isinstance(character, dict):
        return schema.CharacterSchema(**character)
    return schema.CharacterSchema(
        character_name=character.character_name,
        character_id=character.character_id,
        corporation_id=character.corporation_id,
        corporation_name=character.corporation_name,
        alliance_id=character.alliance_id,
        alliance_name=character.alliance_name,
    )


def _doctrine_statuses(doctrines: dict) -> dict[str, schema.DoctrineStatusSchema]:
    """Convert check results of the skill handler to DoctrineStatusSchema."""
    return {
        name: schema.DoctrineStatusSchema(
            id=data["id"],
            name=name,
            category=data.get("category") or "",
            order=data.get("order", 0),
            skills=[
                schema.DoctrineSkillSchema(skill_name=skill, required_level=level)
                for skill, level in data.get("skills", {}).items()
            ],
        )
        for name, data in doctrines.items()
    }


def _character_skills(character_id: int) -> list[CharacterSkill]:
    """Return the Member Audit skills of a character."""
    return list(
        CharacterSkill.objects.filter(
            character__eve_character__character_id=character_id
        ).select_related("eve_type")
    )


class DoctrineApiEndpoints:
    tags = ["Doctrine"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "{character_id}/doctrines/",
            response={
                HTTPStatus.OK: list[schema.CharacterDoctrines],
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Skill check of all characters of an account",
        )
        def get_doctrines(request: WSGIRequest, character_id: int):
            if character_id == 0:
                character_id = request.user.profile.main_character.character_id
            perms, main = get_main_character(request, character_id)

            if not perms:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied")}

            characters = get_alts_queryset(main)

            # Get the skill lists for the main character
            try:
                skills_list = skill_list_handler.get_user_skill_list(
                    user_id=main.character_ownership.user_id
                )["skills_list"]
            except ObjectDoesNotExist:
                # A character without owner has no account: check it alone
                skills_list = skill_list_handler.check_skill_lists(
                    SkillList.objects.all().order_by("ordering", "name"),
                    [main.character_id],
                )

            # Active skill lists are the ones that are visible in the UI
            visibles = set(
                SkillList.objects.filter(active=True).values_list("name", flat=True)
            )

            doctrines_by_character: dict[int, dict] = defaultdict(dict)
            for character_data in skills_list.values():
                for name, doctrine in character_data["doctrines"].items():
                    if name in visibles:
                        doctrines_by_character[character_data["character_id"]][
                            name
                        ] = doctrine

            return [
                schema.CharacterDoctrines(
                    character=_character_schema(character),
                    doctrines=_doctrine_statuses(
                        doctrines_by_character.get(character.character_id, {})
                    ),
                )
                for character in characters
            ]

        @api.get(
            "{corporation_id}/doctrines/members/",
            response={
                HTTPStatus.OK: schema.CorporationMembersResponse,
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Members of a corporation and the active skill lists",
        )
        def get_corporation_members_list(request: WSGIRequest, corporation_id: int):
            if corporation_id == 0:
                corporation_id = request.user.profile.main_character.corporation_id
            perm, corporation = get_corporation(request, corporation_id)

            if not perm or not corporation:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied")}

            __, main_characters, __ = self._process_corporation_members(
                self._corporation_characters(corporation_id)
            )

            members = [
                schema.CorporationMemberOverview(
                    character=_character_schema(data["character"]),
                    alts=[_character_schema(alt) for alt in data["alts"]] or None,
                )
                for data in main_characters.values()
            ]

            doctrines = [
                schema.ActiveDoctrineOverview(
                    id=skill_list.pk,
                    name=skill_list.name,
                    category=skill_list.category or "",
                    order=skill_list.ordering,
                )
                for skill_list in SkillList.objects.filter(active=True).order_by(
                    "ordering", "name"
                )
            ]

            return HTTPStatus.OK, schema.CorporationMembersResponse(
                corporation_id=corporation.corporation_id,
                corporation_name=corporation.corporation_name,
                members=members,
                doctrines=doctrines,
            )

        @api.post(
            "{corporation_id}/doctrines/audit-members/",
            response={
                HTTPStatus.OK: list[schema.CorporationDoctrines],
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Skill check of selected members of a corporation",
        )
        def audit_corporation_members(
            request: WSGIRequest,
            corporation_id: int,
            data: schema.AuditMembersRequest,
        ):
            if corporation_id == 0:
                corporation_id = request.user.profile.main_character.corporation_id
            perm = get_corporation(request, corporation_id)[0]

            if not perm:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied")}

            return HTTPStatus.OK, self._audit_corporation_members(
                corporation_id=corporation_id,
                character_ids=data.character_ids,
                filters=data.to_filter(),
            )

        @api.get(
            "{corporation_id}/doctrines/view/corporation/",
            response={
                HTTPStatus.OK: list[schema.CorporationDoctrines],
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Skill check of all members of a corporation",
        )
        def get_corporation_doctrines(
            request: WSGIRequest,
            corporation_id: int,
            filters: Query[schema.DoctrineAuditFilter],
        ):
            if corporation_id == 0:
                corporation_id = request.user.profile.main_character.corporation_id
            perm = get_corporation(request, corporation_id)[0]

            if not perm:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied")}

            return HTTPStatus.OK, self._audit_corporation_members(
                corporation_id=corporation_id,
                filters=filters,
            )

        @api.get(
            "{character_id}/doctrines/{pk}/",
            response={
                HTTPStatus.OK: schema.MissingSkillsResponse,
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
                HTTPStatus.NOT_FOUND: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Missing skills of a character for a skill list",
        )
        def get_missing_skills(request: WSGIRequest, character_id: int, pk: int):
            if character_id == 0:
                character_id = request.user.profile.main_character.character_id
            perms = get_main_character(request, character_id)[0]

            if not perms:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied")}

            skill_list = get_skill_list(pk)
            if skill_list is None:
                return HTTPStatus.NOT_FOUND, {"error": _("Skill list not found")}

            character = EveCharacter.objects.get(character_id=character_id)
            # Same level as the skill check: the active level counts
            trained = {
                skill.eve_type.name: skill.active_skill_level
                for skill in _character_skills(character_id)
            }

            missing_skills: list[schema.MissingSkillDetail] = []
            for skill_name, level in skill_list.get_skills().items():
                needed_level = int(level)
                trained_level = trained.get(skill_name, 0)
                if trained_level < needed_level:
                    missing_skills.append(
                        schema.MissingSkillDetail(
                            name=skill_name,
                            trained_level=trained_level,
                            needed_level=needed_level,
                        )
                    )

            return HTTPStatus.OK, schema.MissingSkillsResponse(
                character_id=character_id,
                character_name=character.character_name,
                doctrine_id=skill_list.pk,
                doctrine_name=skill_list.name,
                missing_skills=missing_skills,
                clipboard_export="\n".join(
                    f"{skill.name} {skill.needed_level}" for skill in missing_skills
                ),
            )

        @api.get(
            "doctrines/{pk}/",
            response={
                HTTPStatus.OK: schema.DoctrineDetailResponse,
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
                HTTPStatus.NOT_FOUND: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Skills of a skill list, optionally with the skills of a character",
        )
        def get_doctrine_skills(
            request: WSGIRequest, pk: int, character_id: int | None = None
        ):
            skill_list = get_skill_list(pk)
            if skill_list is None:
                return HTTPStatus.NOT_FOUND, {"error": _("Skill list not found")}

            character_skills: dict[str, int] | None = None
            if character_id and get_main_character(request, character_id)[0]:
                character_skills = {
                    skill.eve_type.name: max(
                        skill.active_skill_level, skill.trained_skill_level
                    )
                    for skill in _character_skills(character_id)
                }

            return HTTPStatus.OK, schema.DoctrineDetailResponse(
                **skill_list_fields(skill_list),
                skills={k: int(v) for k, v in skill_list.get_skills().items()},
                character_skills=character_skills,
            )

    @staticmethod
    def _corporation_characters(corporation_id: int, character_ids=None):
        """Member Audit characters of a corporation, optionally only some accounts."""
        characters = Character.objects.filter(
            eve_character__corporation_id=corporation_id
        )
        if character_ids is not None:
            user_ids = CharacterOwnership.objects.filter(
                character__character_id__in=character_ids
            ).values_list("user_id", flat=True)
            characters = characters.filter(
                Q(eve_character__character_ownership__user_id__in=user_ids)
                | Q(eve_character__character_id__in=character_ids)
            )
        return characters.select_related(
            "eve_character",
            "eve_character__character_ownership__user__profile__main_character",
        )

    def _audit_corporation_members(
        self,
        corporation_id: int,
        character_ids: list[int] | None = None,
        filters: schema.DoctrineAuditFilter | None = None,
    ) -> list[dict[str, Any]]:
        """Skill check of corporation members against the filtered active skill lists."""
        if character_ids is not None and len(character_ids) == 0:
            return []

        filters = filters or schema.DoctrineAuditFilter()
        active_skilllists = list(
            filters.get_skill_lists().values_list("name", flat=True)
        )

        users, main_characters, all_characters = self._process_corporation_members(
            self._corporation_characters(corporation_id, character_ids)
        )

        # Uses the cache of the check results
        skilllists = skill_list_handler.get_users_skill_list(users)

        self._process_user_skills(
            skilllists, main_characters, all_characters, active_skilllists
        )
        return list(main_characters.values())

    @staticmethod
    def _create_character_data(character: EveCharacter) -> dict[str, Any]:
        """Helper function to create character data."""
        return {
            "character_name": character.character_name,
            "character_id": character.character_id,
            "corporation_id": character.corporation_id,
            "corporation_name": character.corporation_name,
            "alliance_id": character.alliance_id,
            "alliance_name": character.alliance_name,
        }

    def _process_corporation_members(self, corporation_characters):
        """Group corporation members by account: users, mains with corp alts, all characters."""
        users = set()
        main_characters = {}
        all_characters = {}
        user_characters = defaultdict(list)

        for member in corporation_characters:
            eve_character = member.eve_character
            all_characters[eve_character.character_id] = self._create_character_data(
                eve_character
            )

            try:
                user = eve_character.character_ownership.user
                main_char = user.profile.main_character
            except ObjectDoesNotExist:
                continue
            if not main_char:
                continue

            users.add(user)
            user_characters[user.id].append(eve_character.character_id)

            if main_char.character_id not in main_characters:
                main_characters[main_char.character_id] = {
                    "user_id": user.id,
                    "character": self._create_character_data(main_char),
                    "alts": [],
                    "doctrines": {},
                }

        # Corporation alts of each main character
        for main_char_id, main_char_data in main_characters.items():
            main_char_data["alts"] = [
                all_characters[cid]
                for cid in user_characters[main_char_data["user_id"]]
                if cid != main_char_id
            ]

        return users, main_characters, all_characters

    def _process_user_skills(
        self, skilllists, main_characters, all_characters, active_skilllists
    ):
        """Add the best doctrine results of each account's corporation characters."""
        corp_character_ids = set(all_characters.keys())
        main_by_user_id = {
            data["user_id"]: char_id for char_id, data in main_characters.items()
        }

        for user_id, corp_data in skilllists.items():
            if not ("data" in corp_data and "skills_list" in corp_data["data"]):
                continue

            main_char_id = main_by_user_id.get(user_id)
            if main_char_id is None:
                continue

            # Filter to corporation characters only
            corp_skills_list = {
                char_key: char_data
                for char_key, char_data in corp_data["data"]["skills_list"].items()
                if char_data["character_id"] in corp_character_ids
            }

            main_characters[main_char_id]["doctrines"] = _doctrine_statuses(
                _collect_user_doctrines(corp_skills_list, active_skilllists)
            )
