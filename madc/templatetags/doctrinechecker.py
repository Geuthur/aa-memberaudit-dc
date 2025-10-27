# Standard Library
import json

# Django
from django import template

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from eveuniverse.models import EveType, EveTypeDogmaAttribute

# AA Memberaudit Doctrine Checker
from madc import __title__
from madc.helpers.skill_handler import SkillListHandler
from madc.models.skillchecker import SkillList

register = template.Library()

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


# pylint: disable=too-many-locals
@register.inclusion_tag("madc/partials/fittings.html", takes_context=True)
def madc_skill_overview(context) -> dict:

    # Third Party
    # pylint: disable=import-outside-toplevel
    from fittings.models import Fitting, FittingItem

    _fit = Fitting.objects.get(id=int(context.request.resolver_match.kwargs["fit_id"]))
    _items = FittingItem.objects.filter(fit=_fit).values_list("type_id", flat=True)

    _skill_ids = [182, 183, 184, 1285, 1289, 1290]
    _level_ids = [277, 278, 279, 1286, 1287, 1288]

    _types = EveTypeDogmaAttribute.objects.filter(
        eve_type_id__in=_items, eve_dogma_attribute_id__in=_skill_ids + _level_ids
    )
    _types = _types | EveTypeDogmaAttribute.objects.filter(
        eve_type_id=_fit.ship_type_type_id,
        eve_dogma_attribute_id__in=_skill_ids + _level_ids,
    )

    required = {}
    skills = {}
    sids = set()
    for t in _types:
        if t.eve_type_id not in required:
            required[t.eve_type_id] = {
                0: {"skill": 0, "level": 0},
                1: {"skill": 0, "level": 0},
                2: {"skill": 0, "level": 0},
                3: {"skill": 0, "level": 0},
                4: {"skill": 0, "level": 0},
                5: {"skill": 0, "level": 0},
            }
        a = t.eve_dogma_attribute_id
        v = t.value
        if a in _skill_ids:
            required[t.eve_type_id][_skill_ids.index(a)]["skill"] = v
        elif a in _level_ids:
            indx = _level_ids.index(a)
            if required[t.eve_type_id][indx]["level"] < v:
                required[t.eve_type_id][indx]["level"] = v

        for t in required.values():
            for skill in t.values():
                if skill["skill"]:
                    if skill["skill"] not in skills:
                        skills[skill["skill"]] = {
                            "skill": skill["skill"],
                            "level": 0,
                            "name": "",
                        }
                        sids.add(skill["skill"])
                    if skill["level"] > skills[skill["skill"]]["level"]:
                        skills[skill["skill"]]["level"] = skill["level"]
    sk_check = {}
    for t in EveType.objects.filter(id__in=list(sids)):
        skills[t.id]["name"] = t.name
        sk_check[t.name] = skills[t.id]["level"]

    char_ids = list(
        context.request.user.character_ownerships.all().values_list(
            "character__character_id", flat=True
        )[:15]
    )

    checks = SkillListHandler().check_skill_lists(
        [SkillList(name="fit", skill_list=json.dumps(sk_check))], char_ids
    )

    for __, d in checks.items():
        del d["skills"]

    response = {
        "skills": list(sorted(skills.values(), key=lambda item: item["name"])),
        "chars": dict(sorted(checks.items())),
    }
    context["skills"] = response
    return context
