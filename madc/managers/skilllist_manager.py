# pylint: disable=import-outside-toplevel
# General is imported locally: models/general.py imports managers (circular import)

# Django
from django.db import models

# Alliance Auth
from allianceauth.authentication.models import User
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo

# AA Memberaudit Doctrine Checker
from madc.providers import logger


def _main_character(user: User) -> EveCharacter | None:
    """Return the main character of the user or None."""
    return getattr(getattr(user, "profile", None), "main_character", None)


def _visible_characters(user: User):
    """
    Characters the user may see.

    Own characters always, characters of the own corporation with corp_access,
    characters of the own alliance with alliance_access, all with full access.
    """
    # AA Memberaudit Doctrine Checker
    from madc.models.general import General

    qs = EveCharacter.objects.get_queryset()
    if General.objects.has_full_access(user):
        logger.debug("Returning all characters for %s.", user)
        return qs.all()

    char = _main_character(user)
    if char is None:
        logger.debug("User %s has no main character. Nothing visible.", user)
        return qs.none()

    query = models.Q(character_ownership__user=user)

    if General.objects.has_corp_access(user):
        query |= models.Q(corporation_id=char.corporation_id)

    # A main character without alliance has alliance_id None: comparing with
    # None would match every character without alliance (IS NULL).
    if General.objects.has_alliance_access(user) and char.alliance_id:
        query |= models.Q(alliance_id=char.alliance_id)

    return qs.filter(query)


class SkillListQuerySet(models.QuerySet):
    def manage_to(self, user: User):
        # AA Memberaudit Doctrine Checker
        from madc.models.general import General

        if not General.objects.has_management_access(user):
            logger.debug("User %s has no permission. Nothing visible.", user)
            return EveCharacter.objects.none()
        return _visible_characters(user)


class SkillListManagerBase(models.Manager):
    def get_queryset(self):
        return SkillListQuerySet(self.model, using=self._db)

    @staticmethod
    def visible_eve_characters(user: User):
        return _visible_characters(user)

    @staticmethod
    def visible_eve_corporations(user: User):
        """
        Corporations the user may see.

        The own corporation with corp_access, the corporations of the own
        alliance with alliance_access, all with full access. Nothing otherwise.
        """
        # AA Memberaudit Doctrine Checker
        from madc.models.general import General

        qs = EveCorporationInfo.objects.get_queryset()
        if General.objects.has_full_access(user):
            logger.debug("Returning all corporations for %s.", user)
            return qs.all()

        char = _main_character(user)
        if char is None:
            logger.debug("User %s has no main character. Nothing visible.", user)
            return qs.none()

        queries = []

        if General.objects.has_corp_access(user):
            queries.append(models.Q(corporation_id=char.corporation_id))

        # Compare the EVE alliance ID: `alliance` is a foreign key, its raw
        # value is not the EVE ID in every Alliance Auth version.
        if General.objects.has_alliance_access(user) and char.alliance_id:
            queries.append(models.Q(alliance__alliance_id=char.alliance_id))

        if not queries:
            logger.debug("User %s has no permission. Nothing visible.", user)
            return qs.none()

        query = queries.pop()
        for q in queries:
            query |= q
        return qs.filter(query)

    def manage_to(self, user):
        return self.get_queryset().manage_to(user)


SkillListManager = SkillListManagerBase.from_queryset(SkillListQuerySet)
