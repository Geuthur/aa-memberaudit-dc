# Django
from django.db import models

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger


from app_utils.logging import LoggerAddTag
# AA Memberaudit Doctrine Checker
from madc import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)

class SkillListQuerySet(models.QuerySet):
    def manage_to(self, user):
        qs = EveCharacter.objects.get_queryset()
        # superusers get all visible
        if user.is_superuser:
            logger.debug("Returning all Data for superuser %s.", user)
            return qs.all()

        if user.has_perm("voicesofwar.admin_access"):
            logger.debug("Returning all Data for %s.", user)
            return qs.all()

        logger.debug("User %s has no permission. Nothing visible.", user)
        return qs.none()


class SkillListManagerBase(models.Manager):
    def get_queryset(self):
        return SkillListQuerySet(self.model, using=self._db)

    @staticmethod
    def visible_eve_characters(user):
        qs = EveCharacter.objects.get_queryset()
        if user.is_superuser:
            logger.debug("Returning all characters for superuser %s.", user)
            return qs.all()

        if user.has_perm("voicesofwar.admin_access"):
            logger.debug("Returning all characters for %s.", user)
            return qs.all()

        try:
            char = user.profile.main_character
            assert char
            # build all accepted queries
            queries = [models.Q(character_ownership__user=user)]

            logger.debug(
                "%s queries for user %s visible chracters.", len(queries), user
            )
            # filter based on queries
            query = queries.pop()
            for q in queries:
                query |= q
            return qs.filter(query)
        except AssertionError:
            logger.debug("User %s has no main character. Nothing visible.", user)
            return qs.none()

    def manage_to(self, user):
        return self.get_queryset().manage_to(user)


SkillListManager = SkillListManagerBase.from_queryset(SkillListQuerySet)