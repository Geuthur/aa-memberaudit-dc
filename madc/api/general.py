"""General API endpoints: user data and navigation menu."""

# Standard Library
from http import HTTPStatus

# Third Party
from ninja import NinjaAPI

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.eveonline.evelinks.eveimageserver import character_portrait_url

# AA Memberaudit Doctrine Checker
from madc.api import schema
from madc.models.general import General


class ApiEndpoints:
    tags = ["General"]

    def __init__(self, api: NinjaAPI):
        @api.get(
            "menu/",
            response={
                HTTPStatus.OK: schema.MenuSchema,
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Get Doctrine Checker navigation menu",
        )
        def get_menu(request: WSGIRequest):
            left_menu: list[schema.MenuLink] = [
                schema.MenuLink(name=_("Doctrines"), link="/"),
            ]

            # Same rule as visible_eve_corporations
            if (
                General.objects.has_corp_access(request.user)
                or General.objects.has_alliance_access(request.user)
                or General.objects.has_full_access(request.user)
            ):
                left_menu.append(
                    schema.MenuLink(
                        name=_("Corporation Doctrines"), link="/corporation/"
                    )
                )

            left_menu.append(schema.MenuLink(name=_("Overview"), link="/overview/"))

            right_menu: list[schema.MenuLink] = []
            if General.objects.has_management_access(request.user):
                right_menu.append(schema.MenuLink(name=_("Manage"), link="/manage/"))

            return {"left_links": left_menu, "right_links": right_menu}

        @api.get(
            "user/",
            response={
                HTTPStatus.OK: schema.UserData,
                HTTPStatus.FORBIDDEN: schema.ErrorSchema,
            },
            tags=self.tags,
            summary="Get current user details and permissions",
        )
        def get_user(request: WSGIRequest):
            user = request.user
            profile = getattr(user, "profile", None)
            main_char = getattr(profile, "main_character", None)

            permissions = {
                "basic_access": General.objects.has_basic_access(user),
                "corp_access": General.objects.has_corp_access(user),
                "alliance_access": General.objects.has_alliance_access(user),
                "manage_access": General.objects.has_management_access(user),
                "admin_access": General.objects.has_admin_access(user),
            }

            return {
                "user_id": user.pk,
                "character_id": main_char.character_id if main_char else 0,
                "character_name": (
                    main_char.character_name if main_char else user.username
                ),
                "corporation_id": main_char.corporation_id if main_char else 0,
                "corporation_name": main_char.corporation_name if main_char else "",
                "alliance_id": main_char.alliance_id if main_char else None,
                "alliance_name": main_char.alliance_name if main_char else None,
                "portrait": (
                    character_portrait_url(main_char.character_id)
                    if main_char
                    else None
                ),
                "is_admin": permissions["admin_access"],
                "permissions": permissions,
            }
