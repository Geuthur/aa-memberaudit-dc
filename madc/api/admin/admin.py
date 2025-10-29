# Standard Library
from typing import Any

# Third Party
from ninja import NinjaAPI

# Django
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.models import UserProfile
from allianceauth.eveonline.models import EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from memberaudit.models import Character

# AA Memberaudit Doctrine Checker
from madc import __title__
from madc.api import schema
from madc.api.helpers import (
    generate_button,
    generate_editable_bool_html,
    generate_editable_html,
    get_manage_permission,
)
from madc.models import SkillList

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


class DoctrineCheckerAdminApiEndpoints:
    tags = ["Doctrine Administration"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "administration/",
            response={200: Any, 403: str},
            tags=self.tags,
        )
        def admin_doctrines(request):
            character_id = request.user.profile.main_character.character_id
            response, __ = get_manage_permission(request, character_id)

            if not response:
                return 403, str(_("Permission Denied"))

            skilllist_obj = SkillList.objects.all().order_by("ordering", "name")

            skilllist_dict = {}

            btn_template = "madc/partials/form/button.html"
            settings_dict = {
                "title": _("Delete Skill Plan"),
                "color": "danger",
                "icon": "fa fa-trash",
                "text": _("Are you sure you want to delete this skill plan?"),
                "modal": "skillplan-delete",
                "action": reverse(
                    viewname="madc:delete_doctrine",
                ),
                "ajax": "action",
            }

            for skill_list in skilllist_obj:
                url_doctrine = reverse(
                    viewname="madc:api:get_doctrine_skills",
                    kwargs={"pk": skill_list.pk},
                )

                skills_html = f'<button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#modalViewDoctrineContainer" data-ajax_doctrine="{url_doctrine}">{len(skill_list.get_skills())} Skills</button>'

                delete_btn = generate_button(
                    pk=skill_list.pk,
                    template=btn_template,
                    queryset=skilllist_obj,
                    settings=settings_dict,
                    request=request,
                )

                skilllist_dict[skill_list.name] = {
                    "name": {
                        "html": generate_editable_html(
                            skill_list,
                            field_name="name",
                            name=skill_list.name,
                            url=reverse(
                                viewname="madc:update_skilllist",
                                kwargs={"pk": skill_list.pk},
                            ),
                            title=_("Enter name"),
                        ),
                        "sort": skill_list.name,
                    },
                    "skills": format_html(skills_html),
                    "active": {
                        "html": generate_editable_bool_html(
                            skill_list,
                            name="active",
                            title=_("Toggle active status"),
                            url=reverse(
                                viewname="madc:update_skilllist",
                                kwargs={"pk": skill_list.pk},
                            ),
                        ),
                        "sort": skill_list.active,
                    },
                    "ordering": {
                        "html": generate_editable_html(
                            skill_list,
                            field_name="ordering",
                            name=str(skill_list.ordering),
                            url=reverse(
                                viewname="madc:update_skilllist",
                                kwargs={"pk": skill_list.pk},
                            ),
                            title=_("Enter ordering"),
                        ),
                        "sort": skill_list.ordering,
                    },
                    "category": {
                        "html": generate_editable_html(
                            skill_list,
                            field_name="category",
                            name=str(skill_list.category),
                            url=reverse(
                                viewname="madc:update_skilllist",
                                kwargs={"pk": skill_list.pk},
                            ),
                            title=_("Enter category"),
                        ),
                        "sort": skill_list.category,
                    },
                    "actions": {
                        "delete": format_html(delete_btn),
                    },
                }

            return skilllist_dict

        @api.get(
            "character/overview/",
            response={200: list[schema.CharacterOverview], 403: str},
            tags=self.tags,
        )
        def get_character_overview(request):
            chars_visible = SkillList.objects.visible_eve_characters(request.user)

            if chars_visible is None:
                return 403, "Permission Denied"

            chars_ids = chars_visible.values_list("character_id", flat=True)

            users_char_ids = UserProfile.objects.filter(
                main_character__isnull=False, main_character__character_id__in=chars_ids
            )

            output = []

            for character in users_char_ids:
                # pylint: disable=broad-exception-caught
                try:
                    character_data = {
                        "character_id": character.main_character.character_id,
                        "character_name": character.main_character.character_name,
                        "corporation_id": character.main_character.corporation_id,
                        "corporation_name": character.main_character.corporation_name,
                        "alliance_id": character.main_character.alliance_id,
                        "alliance_name": character.main_character.alliance_name,
                    }
                    output.append({"character": character_data})
                except AttributeError:
                    continue

            return output

        @api.get(
            "corporation/overview/",
            response={200: list[schema.CorporationOverview], 403: str},
            tags=self.tags,
        )
        def get_corporation_overview(request):
            corps_visible = SkillList.objects.visible_eve_corporations(request.user)

            if corps_visible is None:
                return 403, "Permission Denied"

            # Collect unique corporation IDs from visible corporations
            corp_ids = corps_visible.distinct().values_list("corporation_id", flat=True)

            # Get existing corporation IDs from characters
            existing_corp_ids = (
                Character.objects.filter(
                    eve_character__corporation_id__in=corp_ids,
                )
                .select_related(
                    "eve_character",
                )
                .distinct()
                .values_list("eve_character__corporation_id", flat=True)
            )

            # Get Corporations from Existing Members
            corps = EveCorporationInfo.objects.filter(
                corporation_id__in=existing_corp_ids,
            )

            output = []

            for corporation in corps:
                try:
                    corporation_data = {
                        "corporation_id": corporation.corporation_id,
                        "corporation_name": corporation.corporation_name,
                        "alliance_id": getattr(
                            corporation.alliance, "alliance_id", None
                        ),
                        "alliance_name": getattr(
                            corporation.alliance, "alliance_name", "N/A"
                        ),
                    }
                    output.append({"corporation": corporation_data})
                except AttributeError:
                    continue

            return output
