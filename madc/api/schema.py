# Third Party
from ninja import FilterSchema, Schema

# Django
from django.db.models import Q, QuerySet

# AA Memberaudit Doctrine Checker
from madc.models.skillchecker import SkillList


class Message(Schema):
    message: str


class ErrorSchema(Schema):
    """Error response of an endpoint, e.g. for 403 and 404."""

    error: str


# ---------------------------------------------------------------------------
# General / Navigation / User Schemas
# ---------------------------------------------------------------------------


class MenuLink(Schema):
    name: str
    link: str
    is_external: bool = False
    badge: int | None = None
    has_errors: bool = False


class MenuSchema(Schema):
    left_links: list[MenuLink]
    right_links: list[MenuLink]


class UserData(Schema):
    user_id: int
    character_id: int
    character_name: str
    corporation_id: int
    corporation_name: str
    alliance_id: int | None = None
    alliance_name: str | None = None
    portrait: str | None = None
    is_admin: bool = False
    permissions: dict[str, bool] = {}


# ---------------------------------------------------------------------------
# Character & Corporation Schemas
# ---------------------------------------------------------------------------


class CharacterSchema(Schema):
    character_icon: str | None = None
    character_name: str
    character_id: int
    corporation_id: int
    corporation_name: str
    alliance_id: int | None = None
    alliance_name: str | None = None


class CorporationSchema(Schema):
    corporation_icon: str | None = None
    corporation_id: int
    corporation_name: str
    alliance_icon: str | None = None
    alliance_id: int | None = None
    alliance_name: str | None = None


class CharacterOverviewSchema(CharacterSchema):
    actions: str | None = None


class CorporationOverviewSchema(CorporationSchema):
    actions: str | None = None


class DoctrineSkillSchema(Schema):
    skill_name: str
    required_level: int


class DoctrineStatusSchema(Schema):
    """Check result of a skill list: the skills that are still missing."""

    id: int
    name: str
    category: str
    order: int
    skills: list[DoctrineSkillSchema]


class CharacterDoctrines(Schema):
    character: CharacterSchema
    doctrines: dict[str, DoctrineStatusSchema]


class CorporationDoctrines(Schema):
    character: CharacterSchema
    doctrines: dict[str, DoctrineStatusSchema]
    alts: list[CharacterSchema] | None = None


class CorporationMemberOverview(Schema):
    character: CharacterSchema
    alts: list[CharacterSchema] | None = None


class ActiveDoctrineOverview(Schema):
    id: int
    name: str
    category: str
    order: int


class CorporationMembersResponse(Schema):
    corporation_id: int
    corporation_name: str
    members: list[CorporationMemberOverview]
    doctrines: list[ActiveDoctrineOverview]


class DoctrineAuditFilter(FilterSchema):
    """Filter the active skill lists of a corporation audit."""

    category: str | None = None
    doctrine_ids: list[int] | None = None

    def filter_category(self, value: str | None) -> Q:
        if not value or value == "ALL":
            return Q()
        return Q(category=value)

    def filter_doctrine_ids(self, value: list[int] | None) -> Q:
        if not value:
            return Q()
        return Q(pk__in=value)

    def get_skill_lists(self, base_qs: QuerySet | None = None) -> QuerySet:
        """Return the active skill lists that match the filter."""
        if base_qs is None:
            base_qs = SkillList.objects.filter(active=True)
        return self.filter(base_qs)


class AuditMembersRequest(Schema):
    character_ids: list[int] | None = None
    category: str | None = None
    doctrine_ids: list[int] | None = None

    def to_filter(self) -> DoctrineAuditFilter:
        return DoctrineAuditFilter(
            category=self.category,
            doctrine_ids=self.doctrine_ids,
        )


# ---------------------------------------------------------------------------
# Modal & Management Schemas
# ---------------------------------------------------------------------------


class MissingSkillDetail(Schema):
    name: str
    trained_level: int
    needed_level: int


class MissingSkillsResponse(Schema):
    character_id: int
    character_name: str
    doctrine_id: int
    doctrine_name: str
    missing_skills: list[MissingSkillDetail]
    clipboard_export: str


class DoctrineDetailResponse(Schema):
    id: int
    name: str
    category: str | None = None
    ordering: int
    active: bool
    skills: dict[str, int]
    character_skills: dict[str, int] | None = None


class ManageSkillListSchema(Schema):
    id: int
    name: str
    category: str | None = None
    ordering: int
    active: bool
    skill_count: int


class SkillListCreateRequest(Schema):
    name: str
    category: str | None = None
    ordering: int = 0
    skill_list: str


class SkillListUpdateRequest(Schema):
    name: str | None = None
    category: str | None = None
    ordering: int | None = None
    active: bool | None = None
