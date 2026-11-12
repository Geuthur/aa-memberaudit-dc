"""Hook into Alliance Auth"""

# Django
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

# AA Memberaudit Doctrine Checker
from madc import urls
from madc.models.general import General


class MADoctrineCheckerMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Doctrine Checker"),
            "fas fa-book fa-fw",
            "madc:index",
            navactive=["madc:"],
        )

    def render(self, request):
        """Render the menu item"""

        if General.objects.has_basic_access(request.user):
            return MenuItemHook.render(self, request)

        return ""


@hooks.register("menu_item_hook")
def register_skillchecker_menu():
    """Register the menu item"""

    return MADoctrineCheckerMenuItem()


@hooks.register("url_hook")
def register_urls():
    """Register app urls"""

    return UrlHook(urls, "madc", r"^madc/")
