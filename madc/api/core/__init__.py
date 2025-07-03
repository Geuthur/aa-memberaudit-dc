# pylint: disable=unused-argument
from .skillchecker import DoctrineCheckerApiEndpoints


def setup(api):
    DoctrineCheckerApiEndpoints(api)
