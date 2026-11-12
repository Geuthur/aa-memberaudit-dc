# pylint: disable=import-outside-toplevel
# General is imported locally: models/general.py imports managers (circular import)

# Django
from django.db import models

# Alliance Auth
from allianceauth.authentication.models import User
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo

# AA Memberaudit Doctrine Checker
from madc.providers import logger


class SkillListQuerySet(models.QuerySet):
    def manage_to(self, user: User):
        # AA Memberaudit Doctrine Checker
        from madc.models.general import General

        qs = EveCharacter.objects.get_queryset()
        if General.objects.has_full_access(user):
            logger.debug("Returning all Data for %s.", user)
            return qs.all()

        if General.objects.has_management_access(user):
            try:
                char = user.profile.main_character
                char: EveCharacter

                assert char
                # build all accepted queries
                queries = [models.Q(character_ownership__user=user)]

                if General.objects.has_corp_access(user):
                    queries.append(models.Q(corporation_id=char.corporation_id))

                if General.objects.has_alliance_access(user):
                    queries.append(models.Q(alliance_id=char.alliance_id))

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

        logger.debug("User %s has no permission. Nothing visible.", user)
        return qs.none()


class SkillListManagerBase(models.Manager):
    def get_queryset(self):
        return SkillListQuerySet(self.model, using=self._db)

    @staticmethod
    def visible_eve_characters(user: User):
        # AA Memberaudit Doctrine Checker
        from madc.models.general import General

        qs = EveCharacter.objects.get_queryset()
        if General.objects.has_full_access(user):
            logger.debug("Returning all characters for %s.", user)
            return qs.all()

        try:
            char = user.profile.main_character
            char: EveCharacter

            assert char
            # build all accepted queries
            queries = [models.Q(character_ownership__user=user)]

            if General.objects.has_corp_access(user):
                queries.append(models.Q(corporation_id=char.corporation_id))

            if General.objects.has_alliance_access(user):
                queries.append(models.Q(alliance_id=char.alliance_id))

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

    @staticmethod
    def visible_eve_corporations(user: User):
        # AA Memberaudit Doctrine Checker
        from madc.models.general import General

        qs = EveCorporationInfo.objects.get_queryset()
        if General.objects.has_full_access(user):
            logger.debug("Returning all corporations for %s.", user)
            return qs.all()

        try:
            char = user.profile.main_character
            char: EveCharacter

            assert char
            # build all accepted queries
            queries = [models.Q(corporation_id=char.corporation_id)]

            if General.objects.has_corp_access(user):
                queries.append(models.Q(corporation_id=char.corporation_id))

            if General.objects.has_alliance_access(user):
                queries.append(models.Q(alliance_id=char.alliance_id))

            logger.debug(
                "%s queries for user %s visible corporations.", len(queries), user
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
