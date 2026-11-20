"""Test react_base view access."""

# Standard Library
from http import HTTPStatus

# Django
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

# AA Memberaudit Doctrine Checker
from madc import views
from madc.tests import AuthTestCase
from madc.tests.testdata.app import UserMainFactory


class TestReactBaseAccess(AuthTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.no_access = UserMainFactory(permissions=[])

    def test_react_base_view_should_return_ok_for_authorized_user(self):
        """Test should load react_base SPA view for user with basic_access permission."""
        # Test Data
        request = self.factory.get(reverse("madc:react_base"))
        request.user = self.user

        # Test Action
        response = views.react_base(request=request)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("aa-memberaudit-dc-root", response.content.decode("utf-8"))

    def test_react_base_view_should_redirect_unauthorized_user(self):
        """Test should redirect or deny user without basic_access permission."""
        # Test Data
        request = self.factory.get(reverse("madc:react_base"))
        request.user = self.no_access

        # Test Action
        response = views.react_base(request=request)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_react_base_view_should_redirect_unauthenticated_user(self):
        """Test should redirect unauthenticated user to login."""
        # Test Data
        request = self.factory.get(reverse("madc:react_base"))
        request.user = AnonymousUser()

        # Test Action
        response = views.react_base(request=request)

        # Expected Result
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
