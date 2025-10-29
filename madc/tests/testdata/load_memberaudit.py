"""Generate AllianceAuth test objects from allianceauth.json."""

# Standard Library
import json
from pathlib import Path

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from memberaudit.models import Character


def create_memberaudit(eve_character: EveCharacter, **kwargs) -> Character:
    """Create a memberaudit object for the given character."""
    params = {"eve_character": eve_character}
    params.update(kwargs)
    obj = Character(**params)
    obj.save(ignore_cache=True)
    return obj


def load_memberaudit():
    Character.objects.all().delete()
    create_memberaudit(EveCharacter.objects.get(character_id=1000), is_disabled=False)
    create_memberaudit(EveCharacter.objects.get(character_id=1001), is_disabled=False)
    create_memberaudit(EveCharacter.objects.get(character_id=1002), is_disabled=False)
    create_memberaudit(EveCharacter.objects.get(character_id=1003), is_disabled=False)
