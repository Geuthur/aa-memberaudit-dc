# AA Memberaudit Doctrine Checker
from madc import __title__
from madc.providers import logger
from madc.tests import NoSocketsTestCase


class TestAppLogger(NoSocketsTestCase):
    def test_should_log_with_prefix_and_providers_logger_name(self):
        # when
        with self.assertLogs(logger.logger, level="INFO") as logs:
            logger.info("Test message")
        # then
        self.assertEqual(logs.records[0].name, "madc.providers")
        self.assertEqual(logs.records[0].getMessage(), f"[{__title__}] Test message")
