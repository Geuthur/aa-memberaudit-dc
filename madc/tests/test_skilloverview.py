"""TestView class."""

# Standard Library
from unittest.mock import MagicMock

# Django
from django.template import RequestContext
from django.test import RequestFactory, TestCase, modify_settings
from django.urls import reverse

# Alliance Auth (External Libs)
from app_utils.testing import create_user_from_evecharacter
from eveuniverse.models import EveType

# AA Memberaudit Doctrine Checker
from madc.helpers.skill_handler import fittings_installed
from madc.templatetags.doctrinechecker import madc_skill_overview
from madc.tests.testdata.load_allianceauth import load_allianceauth
from madc.tests.testdata.load_eveuniverse import load_eveuniverse


class TestSkillOverviewView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_allianceauth()
        load_eveuniverse()

        cls.factory = RequestFactory()
        cls.user, cls.character_ownership = create_user_from_evecharacter(
            character_id=1001,
            permissions=["madc.basic_access"],
        )
        cls.user_corp_access, cls.character_ownership_corp = (
            create_user_from_evecharacter(
                character_id=1002,
                permissions=["madc.basic_access", "madc.corp_access"],
            )
        )
        cls.user_admin_access, cls.character_ownership_admin = (
            create_user_from_evecharacter(
                character_id=1003,
                permissions=[
                    "madc.basic_access",
                    "madc.corp_access",
                    "madc.admin_access",
                ],
            )
        )
        cls.user_no_access, cls.character_ownership_no_access = (
            create_user_from_evecharacter(
                character_id=1004,
                permissions=[],
            )
        )
        cls.eve_type = EveType.objects.get(id=17478)

    @modify_settings(INSTALLED_APPS={"remove": "fittings"})
    def test_fittings_installed_should_return_false(self):
        """Test should return false if fittings is not installed."""
        self.assertFalse(fittings_installed())

    @modify_settings(INSTALLED_APPS={"append": "fittings"})
    def test_fittings_installed_should_return_true(self):
        """Test should return true if fittings is installed."""
        self.assertTrue(fittings_installed())

    def test_overview_view(self):
        """Test should load overview templatetags."""
        # given
        # Third Party
        from fittings.models import Fitting

        fitting = Fitting.objects.create(
            name="Test Fitting",
            description="A fitting for testing.",
            ship_type=self.eve_type,
            ship_type_type_id=self.eve_type.id,
        )

        request = self.factory.get(reverse("madc:index"))
        # Patch resolver_match.kwargs
        request.resolver_match = MagicMock()
        request.resolver_match.kwargs = {"fit_id": fitting.pk}
        request.user = self.user
        context = RequestContext(request)
        # when
        response = madc_skill_overview(context=context)
        # then
        skill_names = []
        for ctx in response:
            if isinstance(ctx, dict) and "skills" in ctx:
                skills = ctx["skills"].get("skills", [])
                skill_names = [s.get("name") for s in skills]
        self.assertIn("Mining Barge", skill_names)
