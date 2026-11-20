"""Tests for the permissions of the corporation and character endpoints."""

# Standard Library
from http import HTTPStatus

# Third Party
# AA EVE SDE Factory
from evesde_factory.allianceauth import UserFactory

# Django
from django.core.cache import cache
from django.urls import reverse

# AA Memberaudit Doctrine Checker
from madc.tests import AuthTestCase
from madc.tests.testdata.visibility import (
    VisibilityDataMixin,
    create_user_in_corporation,
)

API_URL = "madc:api"
PERMISSION_DENIED = {"error": "Permission Denied"}

BASIC = "madc.basic_access"
CORP = "madc.corp_access"
ALLIANCE = "madc.alliance_access"
ADMIN = "madc.admin_access"

CORPORATION_ENDPOINTS = (
    ("get", "get_corporation_members_list"),
    ("post", "audit_corporation_members"),
    ("get", "get_corporation_doctrines"),
)


class VisibilityApiTestCase(VisibilityDataMixin, AuthTestCase):
    def setUp(self):
        cache.clear()

    def _corporation_overview(self, user) -> set[int]:
        self.client.force_login(user)
        response = self.client.get(reverse(f"{API_URL}:get_corporation_overview"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        return {row["corporation_id"] for row in response.json()}

    def _account_overview(self, user) -> set[int]:
        self.client.force_login(user)
        response = self.client.get(reverse(f"{API_URL}:get_account_overview"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        return {row["character_id"] for row in response.json()}

    def _corporation_statuses(self, user, corporation_id: int) -> list[int]:
        """Status codes of all corporation endpoints for the corporation."""
        self.client.force_login(user)
        statuses = []
        for method, name in CORPORATION_ENDPOINTS:
            url = reverse(
                f"{API_URL}:{name}", kwargs={"corporation_id": corporation_id}
            )
            if method == "post":
                response = self.client.post(
                    url, data={}, content_type="application/json"
                )
            else:
                response = self.client.get(url)
            statuses.append(response.status_code)
        return statuses


class TestCorporationOverviewPermissions(VisibilityApiTestCase):
    def test_overview_should_be_empty_with_basic_access(self):
        user = create_user_in_corporation(self.corp_own, [BASIC])
        self.assertEqual(self._corporation_overview(user), set())

    def test_overview_should_return_own_corporation_with_corp_access(self):
        user = create_user_in_corporation(self.corp_own, [BASIC, CORP])
        self.assertEqual(
            self._corporation_overview(user), {self.corp_own.corporation_id}
        )

    def test_overview_should_return_alliance_corporations_with_alliance_access(self):
        user = create_user_in_corporation(self.corp_own, [BASIC, ALLIANCE])
        self.assertEqual(
            self._corporation_overview(user),
            {self.corp_own.corporation_id, self.corp_allied.corporation_id},
        )

    def test_overview_should_be_empty_with_alliance_access_without_alliance(self):
        user = create_user_in_corporation(self.corp_lone, [BASIC, ALLIANCE])
        self.assertEqual(self._corporation_overview(user), set())

    def test_overview_should_return_all_corporations_with_admin_access(self):
        user = create_user_in_corporation(self.corp_lone, [BASIC, ADMIN])
        self.assertEqual(
            self._corporation_overview(user),
            {
                self.corp_own.corporation_id,
                self.corp_allied.corporation_id,
                self.corp_foreign.corporation_id,
                self.corp_lone.corporation_id,
                self.corp_lone_other.corporation_id,
            },
        )


class TestAccountOverviewPermissions(VisibilityApiTestCase):
    def test_overview_should_return_alliance_accounts_with_alliance_access(self):
        user = create_user_in_corporation(self.corp_own, [BASIC, ALLIANCE])
        self.assertEqual(
            self._account_overview(user),
            {
                self.main_id(user),
                self.main_id(self.member_own),
                self.main_id(self.member_allied),
            },
        )

    def test_overview_should_return_own_account_with_alliance_access_without_alliance(
        self,
    ):
        user = create_user_in_corporation(self.corp_lone, [BASIC, ALLIANCE])
        self.assertEqual(self._account_overview(user), {self.main_id(user)})


class TestCorporationEndpointPermissions(VisibilityApiTestCase):
    def test_own_corporation_should_return_403_with_basic_access(self):
        user = create_user_in_corporation(self.corp_own, [BASIC])
        for corporation_id in (self.corp_own.corporation_id, 0):
            self.assertEqual(
                self._corporation_statuses(user, corporation_id),
                [HTTPStatus.FORBIDDEN] * 3,
            )

    def test_own_corporation_should_return_200_with_corp_access(self):
        user = create_user_in_corporation(self.corp_own, [BASIC, CORP])
        for corporation_id in (self.corp_own.corporation_id, 0):
            self.assertEqual(
                self._corporation_statuses(user, corporation_id), [HTTPStatus.OK] * 3
            )

    def test_allied_corporation_should_return_403_with_corp_access(self):
        user = create_user_in_corporation(self.corp_own, [BASIC, CORP])
        self.assertEqual(
            self._corporation_statuses(user, self.corp_allied.corporation_id),
            [HTTPStatus.FORBIDDEN] * 3,
        )

    def test_allied_corporation_should_return_200_with_alliance_access(self):
        user = create_user_in_corporation(self.corp_own, [BASIC, ALLIANCE])
        self.assertEqual(
            self._corporation_statuses(user, self.corp_allied.corporation_id),
            [HTTPStatus.OK] * 3,
        )

    def test_foreign_corporation_should_return_403_with_alliance_access(self):
        user = create_user_in_corporation(self.corp_own, [BASIC, ALLIANCE])
        self.assertEqual(
            self._corporation_statuses(user, self.corp_foreign.corporation_id),
            [HTTPStatus.FORBIDDEN] * 3,
        )

    def test_corporations_without_alliance_should_return_403_with_alliance_access(
        self,
    ):
        user = create_user_in_corporation(self.corp_lone, [BASIC, ALLIANCE])
        for corporation in (self.corp_lone, self.corp_lone_other):
            self.assertEqual(
                self._corporation_statuses(user, corporation.corporation_id),
                [HTTPStatus.FORBIDDEN] * 3,
            )

    def test_foreign_corporation_should_return_200_with_admin_access(self):
        user = create_user_in_corporation(self.corp_lone, [BASIC, ADMIN])
        self.assertEqual(
            self._corporation_statuses(user, self.corp_foreign.corporation_id),
            [HTTPStatus.OK] * 3,
        )

    def test_members_should_return_error_body_without_permission(self):
        user = create_user_in_corporation(self.corp_own, [BASIC])
        self.client.force_login(user)
        response = self.client.get(
            reverse(
                f"{API_URL}:get_corporation_members_list",
                kwargs={"corporation_id": self.corp_own.corporation_id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), PERMISSION_DENIED)


class TestCharacterEndpointPermissions(VisibilityApiTestCase):
    def _doctrines_status(self, user, character_id: int) -> int:
        self.client.force_login(user)
        return self.client.get(
            reverse(f"{API_URL}:get_doctrines", kwargs={"character_id": character_id})
        ).status_code

    def test_doctrines_should_return_200_for_alliance_member_with_alliance_access(
        self,
    ):
        user = create_user_in_corporation(self.corp_own, [BASIC, ALLIANCE])
        self.assertEqual(
            self._doctrines_status(user, self.main_id(self.member_allied)),
            HTTPStatus.OK,
        )

    def test_doctrines_should_return_403_for_others_with_alliance_access_without_alliance(
        self,
    ):
        user = create_user_in_corporation(self.corp_lone, [BASIC, ALLIANCE])
        for other in (self.member_lone, self.member_lone_other, self.member_own):
            self.assertEqual(
                self._doctrines_status(user, self.main_id(other)),
                HTTPStatus.FORBIDDEN,
            )

    def test_endpoints_should_redirect_user_without_main_character(self):
        """Alliance Auth requires a main character for all URLs of the app."""
        user = UserFactory(permissions__=[BASIC, CORP, ALLIANCE])
        self.assertEqual(
            self._doctrines_status(user, self.main_id(self.member_own)),
            HTTPStatus.FOUND,
        )
        self.assertEqual(self._doctrines_status(user, 0), HTTPStatus.FOUND)
        self.assertEqual(self._corporation_statuses(user, 0), [HTTPStatus.FOUND] * 3)
