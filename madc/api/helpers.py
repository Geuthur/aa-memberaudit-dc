# Django
from django.core.exceptions import ObjectDoesNotExist

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo

# AA Memberaudit Doctrine Checker
from madc import models


def get_main_character(request, character_id) -> tuple[bool, EveCharacter | None]:
    perms = True
    try:
        main_char = EveCharacter.objects.select_related(
            "character_ownership",
            "character_ownership__user__profile",
            "character_ownership__user__profile__main_character",
        ).get(character_id=character_id)
    except EveCharacter.DoesNotExist:
        return False, None
    try:
        main_char = main_char.character_ownership.user.profile.main_character
    except ObjectDoesNotExist:
        pass

    # check access: the own characters are always part of the visible ones
    visible = models.SkillList.objects.visible_eve_characters(request.user)
    if not visible.filter(pk=main_char.pk).exists():
        perms = False
    return perms, main_char


def get_corporation(request, corporation_id) -> tuple[bool, EveCorporationInfo | None]:
    perms = True
    try:
        corporation = EveCorporationInfo.objects.get(corporation_id=corporation_id)
    except ObjectDoesNotExist:
        return False, None

    # check access
    visible = models.SkillList.objects.visible_eve_corporations(request.user)
    if not visible.filter(pk=corporation.pk).exists():
        perms = False
    return perms, corporation


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


def _collect_user_doctrines(skills_list: dict, active_skilllists: list) -> dict:
    """Collect the best doctrine skill data for the user across all their characters."""
    user_doctrines = {}

    # Process each character's skill data
    for __, character_data in skills_list.items():
        if "doctrines" not in character_data:
            continue

        for doctrine_key, doctrine_data in character_data["doctrines"].items():
            # Filter out inactive skill lists
            if doctrine_key not in active_skilllists:
                continue

            if doctrine_key not in user_doctrines:
                user_doctrines[doctrine_key] = doctrine_data
            else:
                # Take the best result (fewer missing skills) across all chars
                # Empty skills dict means all skills are trained
                current_missing_count = len(doctrine_data.get("skills", {}))
                existing_missing_count = len(
                    user_doctrines[doctrine_key].get("skills", {})
                )

                # Prefer the character with fewer missing skills (0 is best)
                if current_missing_count < existing_missing_count:
                    user_doctrines[doctrine_key] = doctrine_data

    return user_doctrines


def get_skill_list(pk: int) -> models.SkillList | None:
    """Return the skill list or None if it does not exist."""
    return models.SkillList.objects.filter(pk=pk).first()


def skill_list_fields(skill_list: models.SkillList) -> dict:
    """Common fields of a skill list in the API responses."""
    return {
        "id": skill_list.pk,
        "name": skill_list.name,
        "category": skill_list.category,
        "ordering": skill_list.ordering,
        "active": skill_list.active,
    }
