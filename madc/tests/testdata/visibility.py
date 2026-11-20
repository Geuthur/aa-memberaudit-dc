"""Corporations, alliances and users for the visibility tests."""

# Third Party
# AA EVE SDE Factory
from evesde_factory.allianceauth import (
    EveAllianceInfoFactory,
    EveCharacterFactory,
    EveCorporationInfoFactory,
)

# AA Memberaudit Doctrine Checker
from madc.tests.testdata.app import UserMainFactory
from madc.tests.testdata.load_memberaudit import create_memberaudit


def create_user_in_corporation(corporation, permissions: list[str]):
    """Create a user whose main character is a Member Audit character of the corporation."""
    character = EveCharacterFactory(corporation=corporation)
    user = UserMainFactory(
        permissions__=permissions, main_character__character=character
    )
    create_memberaudit(character)
    return user


class VisibilityDataMixin:
    """
    Two corporations of one alliance, one of another alliance and two without alliance.

    Every corporation has one member with `basic_access` and a Member Audit character.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # A leading alliance without corporations: primary keys and EVE IDs of
        # the alliances differ, however the database counts.
        EveAllianceInfoFactory()
        cls.alliance = EveAllianceInfoFactory()
        cls.corp_own = EveCorporationInfoFactory(alliance=cls.alliance)
        cls.corp_allied = EveCorporationInfoFactory(alliance=cls.alliance)
        cls.corp_foreign = EveCorporationInfoFactory()
        cls.corp_lone = EveCorporationInfoFactory(create_alliance=False)
        cls.corp_lone_other = EveCorporationInfoFactory(create_alliance=False)

        cls.member_own = create_user_in_corporation(cls.corp_own, ["madc.basic_access"])
        cls.member_allied = create_user_in_corporation(
            cls.corp_allied, ["madc.basic_access"]
        )
        cls.member_foreign = create_user_in_corporation(
            cls.corp_foreign, ["madc.basic_access"]
        )
        cls.member_lone = create_user_in_corporation(
            cls.corp_lone, ["madc.basic_access"]
        )
        cls.member_lone_other = create_user_in_corporation(
            cls.corp_lone_other, ["madc.basic_access"]
        )

    @staticmethod
    def main_id(user) -> int:
        return user.profile.main_character.character_id
