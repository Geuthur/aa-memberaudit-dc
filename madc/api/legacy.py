"""
Endpoint for the jQuery administration page.

Transitional: the React frontend replaces the page and this module.
"""

# Standard Library
from typing import Any

# Third Party
from ninja import NinjaAPI

# Django
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

# AA Memberaudit Doctrine Checker
from madc.api import schema
from madc.api.helpers import (
    generate_button,
    generate_editable_bool_html,
    generate_editable_html,
    get_manage_permission,
)
from madc.models import SkillList


class LegacyApiEndpoints:
    tags = ["Doctrine Administration"]

    # pylint: disable=too-many-statements
    def __init__(self, api: NinjaAPI):
        @api.get(
            "administration/",
            response={200: Any, 403: schema.ErrorSchema},
            tags=self.tags,
        )
        def admin_doctrines(request):
            character_id = request.user.profile.main_character.character_id
            response, __ = get_manage_permission(request, character_id)

            if not response:
                return 403, {"error": gettext("Permission Denied")}

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
                    viewname="madc:doctrine_skills_modal",
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
