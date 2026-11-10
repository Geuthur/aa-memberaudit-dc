# AA Memberaudit Doctrine Checker
from madc.decorators import (
    log_timing,
)
from madc.providers import logger
from madc.tests import NoSocketsTestCase


class TestDecorators(NoSocketsTestCase):
    def test_log_timing(self):
        # given
        @log_timing(logger)
        def trigger_log_timing():
            return "Log Timing"

        # when
        result = trigger_log_timing()
        # then
        self.assertEqual(result, "Log Timing")
