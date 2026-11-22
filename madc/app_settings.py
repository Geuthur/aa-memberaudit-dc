"""
App Settings
"""

# Django
from django.conf import settings

# Set Naming on Auth Hook
AA_MADC_APP_NAME = getattr(settings, "AA_DC_APP_NAME", "Doctrine Checker")
