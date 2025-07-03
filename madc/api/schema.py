# Third Party
from ninja import Schema


class Message(Schema):
    message: str


class Character(Schema):
    character_name: str
    character_id: int
    corporation_id: int
    corporation_name: str
    alliance_id: int | None = None
    alliance_name: str | None = None


class CharacterDoctrines(Schema):
    character: Character
    doctrines: dict
    # skills: dict
