"""App URLs"""

# Django
from django.urls import path, re_path

# AA Memberaudit Doctrine Checker
from madc import views
from madc.api import api

app_name: str = "madc"

urlpatterns = [
    # -- Main URLs
    path("view/index/", views.index, name="index"),
    path(
        "<int:character_id>/view/checker/",
        views.checker,
        name="checker",
    ),
    path(
        "<int:character_id>/view/add/",
        views.doctrine,
        name="add_doctrine",
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
    # -- API System
    re_path(r"^api/", api.urls),
]
