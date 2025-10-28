# Standard Library
import json

# Django
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from eveuniverse.models import EveType

# AA Memberaudit Doctrine Checker
from madc import __title__
from madc.managers.skilllist_manager import SkillListManager

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def skillvalidator(value):
    """
    Custom validator to check if the skill list is valid JSON.
    """
    try:
        skills = json.loads(value)
        for skill, level in skills.items():
            if not EveType.objects.filter(
                name=skill, eve_group__eve_category_id=16
            ).exists():
                raise ValidationError(
                    _("{skill} is not a valid skill.").format(skill=skill)
                )
            try:
                lvl = int(level)
            except ValueError as exc:
                raise ValidationError(
                    _("{skill} level must be an integer.").format(skill=skill)
                ) from exc
            if lvl < 0 or lvl > 5:
                raise ValidationError(
                    _("{skill} level must be between 0 and 5.").format(skill=skill)
                )
    except ValueError as exc:
        raise ValidationError(
            _("Please provide a valid skill list in JSON format.")
        ) from exc


class SkillList(models.Model):
    last_update = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=50, null=True, default=None)
    skill_list = models.TextField(null=True, default="", validators=[skillvalidator])
    ordering = models.IntegerField(
        default=0, validators=[MinValueValidator(0)], verbose_name=_("Order Weight")
    )
    active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_(
            "If unchecked, this skill list will not be used in the skill checker."
        ),
    )
    category = models.CharField(
        max_length=20,
        null=True,
        default=None,
        verbose_name=_("Category"),
        help_text=_("Category of the skill list, used for grouping."),
    )

    objects = SkillListManager()

    def __str__(self):
        return f"{self.name} ({self.ordering})"

    def get_skills(self):
        """Return the skills in the skill list as a dictionary."""
        return json.loads(self.skill_list)

    class Meta:
        default_permissions = ()
