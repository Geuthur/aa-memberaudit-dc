# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from app_utils.testing import NoSocketsTestCase

# AA Memberaudit Doctrine Checker
from madc import __title__
from madc.decorators import (
    log_timing,
)


class TestDecorators(NoSocketsTestCase):
    def test_log_timing(self):
        # given
        logger = LoggerAddTag(get_extension_logger(__name__), __title__)

        @log_timing(logger)
        def trigger_log_timing():
            return "Log Timing"

        # when
        result = trigger_log_timing()
        # then
        self.assertEqual(result, "Log Timing")
