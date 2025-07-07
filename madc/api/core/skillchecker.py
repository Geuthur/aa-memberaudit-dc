# Standard Library
from typing import Any

# Third Party
from ninja import NinjaAPI

# Django
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.models import UserProfile
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Memberaudit Doctrine Checker
from madc import __title__, providers
from madc.api import schema
from madc.api.helpers import (
    generate_button,
    get_alts_queryset,
    get_main_character,
    get_manage_permission,
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
                return 403, _("Permission Denied")

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

        # pylint: disable=too-many-locals
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
                return 403, _("Permission Denied")

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
            character_skills = None
            for __, character_data in user_skilllists["skills_list"].items():
                if character_data["character_id"] == character_id:
                    character_skills = character_data["skills"]
                    break

            if character_skills is None:
                return 403, _("Character not found in skill lists")

            # Compare required skills with character skills
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

            context = {"doctrine": skilllist, "skills": missing_skills}

            return render(request, "madc/partials/modals/missing.html", context=context)

        # pylint: disable=too-many-locals
        @api.get(
            "doctrines/{pk}/",
            response={200: Any, 403: str},
            tags=self.tags,
        )
        def get_doctrine_skills(request, pk: int):
            perms = request.user.has_perm("madc.basic_access")

            if not perms:
                return 403, _("Permission Denied")

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

        @api.get(
            "administration/",
            response={200: Any, 403: str},
            tags=self.tags,
        )
        def admin_doctrines(request):
            character_id = request.user.profile.main_character.character_id
            response, __ = get_manage_permission(request, character_id)

            if not response:
                return 403, _("Permission Denied")

            skilllist_obj = SkillList.objects.all().order_by("ordering", "name")

            skilllist_dict = {}

            btn_template = "madc/partials/form/button.html"
            url = reverse(
                viewname="madc:delete_doctrine",
            )

            settings_dict = {
                "title": _("Delete Skill Plan"),
                "color": "danger",
                "icon": "fa fa-trash",
                "text": _("Are you sure you want to delete this skill plan?"),
                "modal": "skillplan-delete",
                "action": url,
                "ajax": "action",
            }

            for skill_list in skilllist_obj:
                edit_btn = generate_button(
                    pk=skill_list.pk,
                    template=btn_template,
                    queryset=skilllist_obj,
                    settings=settings_dict,
                    request=request,
                )
                url = reverse(
                    viewname="madc:update_skilllist",
                    kwargs={"pk": skill_list.pk},
                )
                url_doctrine = reverse(
                    viewname="madc:api:get_doctrine_skills",
                    kwargs={"pk": skill_list.pk},
                )

                # Get translated texts
                active_text = _("Active")
                inactive_text = _("Inactive")
                enter_name_text = _("Enter name")
                enter_category_text = _("Enter category")
                enter_ordering_text = _("Enter ordering")

                name_html = f"<a class='editable' href='#' data-type='text' data-pk='{skill_list.pk}' data-name='name' data-url='{url}' data-title='{enter_name_text}'>{skill_list.name}</a>"
                skills_html = f'<button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#modalViewDoctrineContainer" data-ajax_doctrine="{url_doctrine}">{len(skill_list.get_skills())} Skills</button>'

                # Correctly handle the boolean editable with proper escaping
                if skill_list.active:
                    active_badge = f"<span class='badge bg-success'>{active_text}"
                else:
                    active_badge = f"<span class='badge bg-secondary'>{inactive_text}"
                active_badge += "</span>"

                # Use mark_safe for complex HTML to avoid format_html issues
                active_html = mark_safe(
                    f'<a href="#" class="editable-boolean no_underline" data-type="select" data-pk="{skill_list.pk}" data-name="active" data-url="{url}" data-source=\'[{{"value": true, "text": "{active_text}"}}, {{"value": false, "text": "{inactive_text}"}}]\' data-value="{str(skill_list.active).lower()}">{active_badge}</a>'
                )

                ordering_html = f'<a class="editable" href="#" data-type="text" data-pk="{skill_list.pk}" data-name="ordering" data-url="{url}" data-title="{enter_ordering_text}">{skill_list.ordering}</a>'
                category_html = f'<a class="editable" href="#" data-type="text" data-pk="{skill_list.pk}" data-name="category" data-url="{url}" data-title="{enter_category_text}">{skill_list.category}</a>'

                skilllist_dict[skill_list.name] = {
                    "name": {
                        "html": format_html(name_html),
                        "sort": skill_list.name,
                    },
                    "skills": format_html(skills_html),
                    "active": {
                        "html": active_html,
                        "sort": skill_list.active,
                    },
                    "ordering": {
                        "html": format_html(ordering_html),
                        "sort": skill_list.ordering,
                    },
                    "category": {
                        "html": format_html(category_html),
                        "sort": skill_list.category,
                    },
                    "actions": {
                        "delete": format_html(edit_btn),
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
