"""Generate Member Audit test objects."""

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from memberaudit.models import Character


def create_memberaudit(eve_character: EveCharacter, **kwargs) -> Character:
    """Create a memberaudit object for the given character."""
    params = {"eve_character": eve_character, "is_disabled": False}
    params.update(kwargs)
    obj = Character(**params)
    obj.save(ignore_cache=True)
    return obj
