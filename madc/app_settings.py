"""
App Settings
"""

# Standard Library
import sys

# Alliance Auth (External Libs)
from app_utils.app_settings import clean_setting

IS_TESTING = sys.argv[1:2] == ["test"]

# EVE Online Swagger
EVE_BASE_URL = "https://esi.evetech.net/"
EVE_API_URL = "https://esi.evetech.net/latest/"
EVE_BASE_URL_REGEX = r"^http[s]?:\/\/esi.evetech\.net\/"

# Set Naming on Auth Hook
AA_MADC_APP_NAME = clean_setting("AA_DC_APP_NAME", "Doctrine Checker")

# Task Settings
# Global timeout for tasks in seconds to reduce task accumulation during outages.
AA_MADC_TASKS_TIME_LIMIT = clean_setting("AA_MADC_TASKS_TIME_LIMIT", 7200)
