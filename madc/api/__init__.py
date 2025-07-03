# Third Party
from ninja import NinjaAPI
from ninja.security import django_auth

# Django
from django.conf import settings

# AA Memberaudit Doctrine Checker
from madc.api import core

api = NinjaAPI(
    title="AA Memberaudit Doctrine Checker API",
    version="0.1.0",
    urls_namespace="madc:api",
    auth=django_auth,
    csrf=True,
    openapi_url=settings.DEBUG and "/openapi.json" or "",
)

# Add the core endpoints
core.setup(api)
