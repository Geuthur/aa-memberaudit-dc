"""App Tasks"""

# Standard Library
# Third Party
from celery import shared_task

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger
from allianceauth.services.tasks import QueueOnce

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Memberaudit Doctrine Checker
from madc import __title__, app_settings
from madc.decorators import when_esi_is_available

logger = LoggerAddTag(get_extension_logger(__name__), __title__)

MAX_RETRIES_DEFAULT = 3

# Default params for all tasks.
TASK_DEFAULTS = {
    "time_limit": app_settings.AA_MADC_TASKS_TIME_LIMIT,
    "max_retries": MAX_RETRIES_DEFAULT,
}

# Default params for tasks that need run once only.
TASK_DEFAULTS_ONCE = {**TASK_DEFAULTS, **{"base": QueueOnce}}

_update_madc_params = {
    **TASK_DEFAULTS_ONCE,
    **{"once": {"keys": ["corporation_id", "force_refresh"], "graceful": True}},
}


# pylint: disable=unused-argument
# Template - Tasks
@shared_task(**TASK_DEFAULTS_ONCE)
@when_esi_is_available
def doctrine_template(runs: int = 0, force_refresh: bool = False):
    pass
