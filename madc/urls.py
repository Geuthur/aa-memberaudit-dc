"""App URLs"""

# Django
from django.urls import path, re_path

# Alliance Auth
from allianceauth.authentication.decorators import decorate_url_patterns

# AA Memberaudit Doctrine Checker
from madc import views
from madc.api import api
from madc.api.auth import basic_access_required

app_name: str = "madc"  # pylint: disable=invalid-name

# Every URL of the API (endpoints, schema and docs) requires `basic_access`
api_patterns, api_app_name, api_namespace = api.urls
api_patterns = decorate_url_patterns(
    (api_patterns, api_app_name), basic_access_required
)[0]

urlpatterns = [
    # -- Main URLs
    path("view/index/", views.index, name="index"),
    path(
        "<int:character_id>/view/checker/",
        views.checker,
        name="checker",
    ),
    path(
        "<int:corporation_id>/view/corporation_checker/",
        views.corporation_checker,
        name="corporation_checker",
    ),
    path(
        "<int:character_id>/view/add/",
        views.doctrine,
        name="add_doctrine",
    ),
    path(
        "<int:character_id>/view/overview/",
        views.overview,
        name="overview",
    ),
    path(
        "<int:character_id>/view/corporation_overview/",
        views.corporation_overview,
        name="corporation_overview",
    ),
    path(
        "<int:character_id>/view/administration/",
        views.administration,
        name="administration",
    ),
    # -- Administration
    path(
        "admin/add/",
        views.ajax_doctrine,
        name="ajax_doctrine",
    ),
    path(
        "admin/delete/",
        views.delete_doctrine,
        name="delete_doctrine",
    ),
    path(
        "admin/update/<int:pk>/",
        views.edit_doctrine,
        name="update_skilllist",
    ),
    # -- API System
    re_path(r"^api/", (api_patterns, api_app_name, api_namespace)),
]
