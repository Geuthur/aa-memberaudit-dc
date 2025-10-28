# Standard Library
import sys
import time

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Memberaudit Doctrine Checker
from madc import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)

# True when tests are currently running, else False.
IS_TESTING = sys.argv[1:2] == ["test"]


def log_timing(logs):
    """
    Ein Dekorator, der die Ausführungszeit einer Funktion misst und in die Logdatei schreibt.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            logs.debug(
                "TIME: %s run for %s seconds with args: %s",
                end_time - start_time,
                func.__name__,
                args,
            )
            return result

        return wrapper

    return decorator
