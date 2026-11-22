"""Tests for the auth hooks."""

# Standard Library
from unittest.mock import patch

# Django
from django.test import TestCase

# AA Memberaudit Doctrine Checker
from madc import app_settings
from madc.auth_hooks import MADoctrineCheckerMenuItem


class TestMenuItemName(TestCase):
    def test_menu_item_should_use_default_name(self):
        """Test should show the default app name in the menu."""
        # Test Action
        menu_item = MADoctrineCheckerMenuItem()

        # Expected Result
        self.assertEqual(menu_item.text, "Doctrine Checker")

    def test_menu_item_should_use_app_name_setting(self):
        """Test should show the configured app name in the menu."""
        # Test Action
        with patch.object(app_settings, "AA_MADC_APP_NAME", "Fit Check"):
            menu_item = MADoctrineCheckerMenuItem()

        # Expected Result
        self.assertEqual(menu_item.text, "Fit Check")
