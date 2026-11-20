# Third Party
from ninja import NinjaAPI
from ninja.security import django_auth

# Django
from django.conf import settings

# AA Memberaudit Doctrine Checker
from madc.api import doctrine, general, manage

api = NinjaAPI(
    title="AA Memberaudit Doctrine Checker API",
    version="0.1.0",
    urls_namespace="madc:api",
    auth=django_auth,
    openapi_url=settings.DEBUG and "/openapi.json" or "",
)


def setup(ninja_api):
    """Setup API endpoints."""
    general.ApiEndpoints(ninja_api)
    manage.ManageApiEndpoints(ninja_api)
    doctrine.DoctrineApiEndpoints(ninja_api)


# Initialize API endpoints
setup(api)
