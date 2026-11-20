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
    # -- API System
    re_path(r"^api/", (api_patterns, api_app_name, api_namespace)),
    # -- Bookmarks of the template pages before the React frontend
    path("view/index/", views.legacy_redirect),
    path("<int:pk>/view/checker/", views.legacy_redirect, {"page": "doctrine"}),
    path(
        "<int:pk>/view/corporation_checker/",
        views.legacy_redirect,
        {"page": "corporation"},
    ),
    path("<int:pk>/view/overview/", views.legacy_redirect, {"page": "overview"}),
    path(
        "<int:pk>/view/corporation_overview/",
        views.legacy_redirect,
        {"page": "overview"},
    ),
    path("<int:pk>/view/add/", views.legacy_redirect, {"page": "manage"}),
    path("<int:pk>/view/administration/", views.legacy_redirect, {"page": "manage"}),
    # -- React Frontend SPA
    path("", views.react_base, name="react_base"),
    re_path(
        r"^(?!api/).*$",
        views.react_base,
        name="react_base_catchall",
    ),
]
