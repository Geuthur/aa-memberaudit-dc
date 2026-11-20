"""App Views"""

# Django
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required

# AA Memberaudit Doctrine Checker
from madc import __version__


@login_required
@permissions_required(["madc.basic_access"])
def react_base(
    request: WSGIRequest, *args, **kwargs
):  # pylint: disable=unused-argument
    """React Frontend SPA Base View."""
    context = {
        "app_name": "madc",
        "title": _("Doctrine Checker"),
        "version": __version__,
    }
    return render(request, "madc/react_madc.html", context=context)
