"""Shared ESI client for Memberaudit Doctrine Checker."""

# Alliance Auth
from esi.clients import EsiClientProvider

# AA Memberaudit Doctrine Checker
from madc import __app_name_useragent__, __github_url__, __version__
from madc.helpers.skill_handler import SkillListHandler

esi = EsiClientProvider(
    ua_appname=__app_name_useragent__, ua_version=__version__, ua_url=__github_url__
)
skills = SkillListHandler()
