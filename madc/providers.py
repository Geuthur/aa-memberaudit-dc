"""Shared ESI client for Memberaudit Doctrine Checker."""

# Alliance Auth
from esi.clients import EsiClientProvider

# AA Memberaudit Doctrine Checker
from madc.constants import USER_AGENT
from madc.helpers.skill_handler import SkillListHandler

esi = EsiClientProvider(app_info_text=USER_AGENT)
skills = SkillListHandler()
