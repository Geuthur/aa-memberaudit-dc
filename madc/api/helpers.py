# Django
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Memberaudit Doctrine Checker
from madc import __title__, models

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def get_manage_permission(request, character_id):
    """Check if the user has permission to manage."""
    perms = True
    main_char = EveCharacter.objects.select_related(
        "character_ownership",
        "character_ownership__user__profile",
        "character_ownership__user__profile__main_character",
    ).get(character_id=character_id)
    try:
        main_char = main_char.character_ownership.user.profile.main_character
    except ObjectDoesNotExist:
        pass

    # check access
    visible = models.SkillList.objects.manage_to(request.user)
    if main_char not in visible:
        account_chars = (
            request.user.profile.main_character.character_ownership.user.character_ownerships.all()
        )
        if main_char in account_chars:
            pass
        else:
            perms = False
    return perms, main_char


def get_main_character(request, character_id):
    perms = True
    main_char = EveCharacter.objects.select_related(
        "character_ownership",
        "character_ownership__user__profile",
        "character_ownership__user__profile__main_character",
    ).get(character_id=character_id)
    try:
        main_char = main_char.character_ownership.user.profile.main_character
    except ObjectDoesNotExist:
        pass

    # check access
    visible = models.SkillList.objects.visible_eve_characters(request.user)
    if main_char not in visible:
        account_chars = (
            request.user.profile.main_character.character_ownership.user.character_ownerships.all()
        )
        if main_char in account_chars:
            pass
        else:
            perms = False
    return perms, main_char


def get_alts_queryset(main_char):
    try:
        linked_characters = (
            main_char.character_ownership.user.character_ownerships.all().values_list(
                "character_id", flat=True
            )
        )

        return EveCharacter.objects.filter(id__in=linked_characters)
    except ObjectDoesNotExist:
        return EveCharacter.objects.filter(pk=main_char.pk)


def generate_button(pk: int, template, queryset, settings, request) -> mark_safe:
    """Generate a html button for the tax system"""
    return format_html(
        render_to_string(
            template,
            {
                "pk": pk,
                "queryset": queryset,
                "settings": settings,
            },
            request=request,
        )
    )