# pylint: disable=unused-argument
from .admin import DoctrineCheckerAdminApiEndpoints


def setup(api):
    DoctrineCheckerAdminApiEndpoints(api)
