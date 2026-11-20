"""App Views"""

# Django
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
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


def legacy_redirect(
    request: WSGIRequest, pk: int = 0, page: str = ""
):  # pylint: disable=unused-argument
    """Redirect a URL of the former template pages to its React page."""
    url = reverse("madc:react_base")
    if page:
        url += f"{page}/"
        # The ID 0 stood for the own character or corporation
        if page in ("doctrine", "corporation") and pk:
            url += f"{pk}/"
    return HttpResponseRedirect(url)
