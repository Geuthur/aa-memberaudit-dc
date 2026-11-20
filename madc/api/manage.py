"""Manage API endpoints: skill lists and overviews of accounts and corporations."""

# Standard Library
import json
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.authentication.models import UserProfile
from allianceauth.eveonline.evelinks.eveimageserver import (
    alliance_logo_url,
    character_portrait_url,
    corporation_logo_url,
)
from allianceauth.eveonline.models import EveCorporationInfo

# Alliance Auth (External Libs)
from memberaudit.models import Character

# AA Memberaudit Doctrine Checker
from madc import forms
from madc.api import schema
from madc.api.helpers import get_skill_list, skill_list_fields
from madc.models import SkillList
from madc.models.general import General
from madc.providers import logger

NAME_MAX_LENGTH = SkillList._meta.get_field("name").max_length
CATEGORY_MAX_LENGTH = SkillList._meta.get_field("category").max_length
ORDERING_MAX = 999


def _manage_schema(skill_list: SkillList) -> schema.ManageSkillListSchema:
    return schema.ManageSkillListSchema(
        **skill_list_fields(skill_list),
        skill_count=len(skill_list.get_skills()),
    )


def _form_errors(form: forms.SkillListForm) -> str:
    """Join the errors of a form, prefixed with the field label."""
    messages = []
    for field, errors in form.errors.items():
        for error in errors:
            if field == "__all__":
                messages.append(str(error))
            else:
                label = form.fields[field].label or field
                messages.append(f"{label}: {error}")
    return " ".join(messages)


# pylint: disable=too-many-return-statements
def _apply_update(
    skill_list: SkillList, payload: schema.SkillListUpdateRequest
) -> str | None:
    """Apply the given fields to the skill list. Return an error text or None."""
    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            return _("Name cannot be empty")
        if len(name) > NAME_MAX_LENGTH:
            return _("Name can have at most {max} characters").format(
                max=NAME_MAX_LENGTH
            )
        if (
            SkillList.objects.filter(name__iexact=name)
            .exclude(pk=skill_list.pk)
            .exists()
        ):
            return _("Skill list with this name already exists")
        skill_list.name = name

    if payload.category is not None:
        # None leaves the category as it is, an empty text removes it
        category = payload.category.strip()
        if len(category) > CATEGORY_MAX_LENGTH:
            return _("Category can have at most {max} characters").format(
                max=CATEGORY_MAX_LENGTH
            )
        skill_list.category = category or None

    if payload.ordering is not None:
        if not 0 <= payload.ordering <= ORDERING_MAX:
            return _("Ordering must be between 0 and 999")
        skill_list.ordering = payload.ordering

    if payload.active is not None:
        skill_list.active = payload.active

    return None


class ManageApiEndpoints:
    tags = ["Manage"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "manage/",
            response={
                HTTPStatus.OK: list[schema.ManageSkillListSchema],
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="List all skill lists for management",
        )
        def manage_skilllists(request: WSGIRequest):
            if not General.objects.has_management_access(request.user):
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied")}

            return HTTPStatus.OK, [
                _manage_schema(skill_list)
                for skill_list in SkillList.objects.order_by("ordering", "name")
            ]

        @api.post(
            "manage/skilllist/",
            response={
                HTTPStatus.CREATED: schema.ManageSkillListSchema,
                HTTPStatus.BAD_REQUEST: schema.ErrorSchema,
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Create a skill list from a skill plan",
        )
        def create_skilllist(
            request: WSGIRequest, payload: schema.SkillListCreateRequest
        ):
            if not General.objects.has_management_access(request.user):
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied")}

            form = forms.SkillListForm(
                {
                    "name": payload.name,
                    "category": payload.category or "",
                    "ordering": payload.ordering,
                    "skill_list": payload.skill_list,
                }
            )
            if not form.is_valid():
                return HTTPStatus.BAD_REQUEST, {"error": _form_errors(form)}

            if SkillList.objects.filter(
                name__iexact=form.cleaned_data["name"]
            ).exists():
                return HTTPStatus.BAD_REQUEST, {
                    "error": _("Skill list with this name already exists")
                }

            parsed_skills = form.get_parsed_skills()
            if not parsed_skills:
                return HTTPStatus.BAD_REQUEST, {
                    "error": _("Your skill plan is empty. Please add skills.")
                }

            ordering = form.cleaned_data["ordering"]
            skill_list = SkillList.objects.create(
                name=form.cleaned_data["name"],
                skill_list=json.dumps(parsed_skills, ensure_ascii=False),
                category=form.cleaned_data["category"] or None,
                ordering=ordering if ordering is not None else 0,
            )
            logger.info(
                "Skilllist %s created by %s", skill_list.name, request.user.username
            )
            return HTTPStatus.CREATED, _manage_schema(skill_list)

        @api.put(
            "manage/skilllist/{pk}/",
            response={
                HTTPStatus.OK: schema.ManageSkillListSchema,
                HTTPStatus.BAD_REQUEST: schema.ErrorSchema,
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
                HTTPStatus.NOT_FOUND: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Update name, category, ordering or active flag of a skill list",
        )
        def update_skilllist(
            request: WSGIRequest, pk: int, payload: schema.SkillListUpdateRequest
        ):
            if not General.objects.has_management_access(request.user):
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied")}

            skill_list = get_skill_list(pk)
            if skill_list is None:
                return HTTPStatus.NOT_FOUND, {"error": _("Skill list not found")}

            error = _apply_update(skill_list, payload)
            if error:
                return HTTPStatus.BAD_REQUEST, {"error": error}

            skill_list.save()
            logger.info(
                "Skilllist %s updated by %s with %s",
                skill_list.name,
                request.user.username,
                payload.dict(exclude_none=True),
            )
            return HTTPStatus.OK, _manage_schema(skill_list)

        @api.delete(
            "manage/skilllist/{pk}/",
            response={
                HTTPStatus.OK: schema.Message,
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
                HTTPStatus.NOT_FOUND: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Delete a skill list",
        )
        def delete_skilllist(request: WSGIRequest, pk: int):
            if not General.objects.has_management_access(request.user):
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied")}

            skill_list = get_skill_list(pk)
            if skill_list is None:
                return HTTPStatus.NOT_FOUND, {"error": _("Skill list not found")}

            name = skill_list.name
            skill_list.delete()
            logger.info("Skilllist %s deleted by %s", name, request.user.username)
            return HTTPStatus.OK, {
                "message": _("Skilllist: {name} deleted").format(name=name)
            }

        @api.get(
            "account/overview/",
            response={
                HTTPStatus.OK: list[schema.CharacterOverviewSchema],
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Overview of the visible accounts",
        )
        def get_account_overview(request: WSGIRequest):
            chars_visible = SkillList.objects.visible_eve_characters(request.user)

            if chars_visible is None:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied")}

            accounts = UserProfile.objects.filter(
                main_character__isnull=False,
                main_character__character_id__in=chars_visible.values_list(
                    "character_id", flat=True
                ),
            ).select_related("main_character")

            return HTTPStatus.OK, [
                schema.CharacterOverviewSchema(
                    character_icon=character_portrait_url(char.character_id, 32),
                    character_name=char.character_name,
                    character_id=char.character_id,
                    corporation_id=char.corporation_id,
                    corporation_name=char.corporation_name,
                    alliance_id=char.alliance_id,
                    alliance_name=char.alliance_name,
                    actions=f"/doctrine/{char.character_id}/",
                )
                for char in (account.main_character for account in accounts)
            ]

        @api.get(
            "corporation/overview/",
            response={
                HTTPStatus.OK: list[schema.CorporationOverviewSchema],
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Overview of the visible corporations with Member Audit characters",
        )
        def get_corporation_overview(request: WSGIRequest):
            corps_visible = SkillList.objects.visible_eve_corporations(request.user)

            if corps_visible is None:
                return HTTPStatus.FORBIDDEN, {"error": _("Permission Denied")}

            corp_ids = corps_visible.distinct().values_list("corporation_id", flat=True)

            # Only corporations with Member Audit characters
            existing_corp_ids = (
                Character.objects.filter(eve_character__corporation_id__in=corp_ids)
                .distinct()
                .values_list("eve_character__corporation_id", flat=True)
            )

            corporations = EveCorporationInfo.objects.filter(
                corporation_id__in=existing_corp_ids
            ).select_related("alliance")

            output = []
            for corporation in corporations:
                alliance_id = getattr(corporation.alliance, "alliance_id", None)
                output.append(
                    schema.CorporationOverviewSchema(
                        corporation_icon=corporation_logo_url(
                            corporation.corporation_id, 32
                        ),
                        corporation_id=corporation.corporation_id,
                        corporation_name=corporation.corporation_name,
                        alliance_icon=(
                            alliance_logo_url(alliance_id, 32) if alliance_id else None
                        ),
                        alliance_id=alliance_id,
                        alliance_name=getattr(
                            corporation.alliance, "alliance_name", None
                        ),
                        actions=f"/corporation/{corporation.corporation_id}/",
                    )
                )
            return HTTPStatus.OK, output
