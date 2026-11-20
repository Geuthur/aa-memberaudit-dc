"""Which characters and corporations a user may see, by permission."""

# Third Party
# AA EVE SDE Factory
from evesde_factory.allianceauth import UserFactory

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo

# AA Memberaudit Doctrine Checker
from madc.models import SkillList
from madc.tests import AuthTestCase
from madc.tests.testdata.visibility import (
    VisibilityDataMixin,
    create_user_in_corporation,
)

BASIC = "madc.basic_access"
CORP = "madc.corp_access"
ALLIANCE = "madc.alliance_access"
MANAGE = "madc.manage_access"
ADMIN = "madc.admin_access"


class TestVisibleCorporations(VisibilityDataMixin, AuthTestCase):
    def _visible(self, user) -> set[int]:
        return set(
            SkillList.objects.visible_eve_corporations(user).values_list(
                "corporation_id", flat=True
            )
        )

    def test_basic_access_should_see_no_corporation(self):
        user = create_user_in_corporation(self.corp_own, [BASIC])
        self.assertEqual(self._visible(user), set())

    def test_manage_access_should_see_no_corporation(self):
        user = create_user_in_corporation(self.corp_own, [BASIC, MANAGE])
        self.assertEqual(self._visible(user), set())

    def test_corp_access_should_see_only_own_corporation(self):
        user = create_user_in_corporation(self.corp_own, [BASIC, CORP])
        self.assertEqual(self._visible(user), {self.corp_own.corporation_id})

    def test_alliance_access_should_see_corporations_of_own_alliance(self):
        user = create_user_in_corporation(self.corp_own, [BASIC, ALLIANCE])
        self.assertEqual(
            self._visible(user),
            {self.corp_own.corporation_id, self.corp_allied.corporation_id},
        )

    def test_alliance_access_should_see_nothing_without_alliance(self):
        user = create_user_in_corporation(self.corp_lone, [BASIC, ALLIANCE])
        self.assertEqual(self._visible(user), set())

    def test_corp_and_alliance_access_should_see_own_corporation_without_alliance(
        self,
    ):
        user = create_user_in_corporation(self.corp_lone, [BASIC, CORP, ALLIANCE])
        self.assertEqual(self._visible(user), {self.corp_lone.corporation_id})

    def test_admin_access_should_see_all_corporations(self):
        user = create_user_in_corporation(self.corp_lone, [BASIC, ADMIN])
        for viewer in (user, self.superuser):
            self.assertEqual(
                SkillList.objects.visible_eve_corporations(viewer).count(),
                EveCorporationInfo.objects.count(),
            )

    def test_user_without_main_should_see_no_corporation(self):
        user = UserFactory(permissions__=[BASIC, CORP, ALLIANCE])
        self.assertEqual(self._visible(user), set())


class TestVisibleCharacters(VisibilityDataMixin, AuthTestCase):
    def _visible(self, user) -> set[int]:
        return set(
            SkillList.objects.visible_eve_characters(user).values_list(
                "character_id", flat=True
            )
        )

    def test_basic_access_should_see_only_own_characters(self):
        user = create_user_in_corporation(self.corp_own, [BASIC])
        self.assertEqual(self._visible(user), {self.main_id(user)})

    def test_corp_access_should_see_characters_of_own_corporation(self):
        user = create_user_in_corporation(self.corp_own, [BASIC, CORP])
        self.assertEqual(
            self._visible(user), {self.main_id(user), self.main_id(self.member_own)}
        )

    def test_alliance_access_should_see_characters_of_own_alliance(self):
        user = create_user_in_corporation(self.corp_own, [BASIC, ALLIANCE])
        self.assertEqual(
            self._visible(user),
            {
                self.main_id(user),
                self.main_id(self.member_own),
                self.main_id(self.member_allied),
            },
        )

    def test_alliance_access_should_see_only_own_characters_without_alliance(self):
        user = create_user_in_corporation(self.corp_lone, [BASIC, ALLIANCE])
        self.assertEqual(self._visible(user), {self.main_id(user)})

    def test_admin_access_should_see_all_characters(self):
        user = create_user_in_corporation(self.corp_lone, [BASIC, ADMIN])
        self.assertEqual(
            SkillList.objects.visible_eve_characters(user).count(),
            EveCharacter.objects.count(),
        )

    def test_user_without_main_should_see_no_character(self):
        user = UserFactory(permissions__=[BASIC, CORP, ALLIANCE])
        self.assertEqual(self._visible(user), set())

    def test_manage_to_should_see_only_own_characters_without_alliance(self):
        user = create_user_in_corporation(self.corp_lone, [BASIC, MANAGE, ALLIANCE])
        self.assertEqual(
            set(
                SkillList.objects.manage_to(user).values_list("character_id", flat=True)
            ),
            {self.main_id(user)},
        )

    def test_manage_to_should_see_nothing_without_manage_access(self):
        user = create_user_in_corporation(self.corp_own, [BASIC, CORP, ALLIANCE])
        self.assertEqual(SkillList.objects.manage_to(user).count(), 0)
