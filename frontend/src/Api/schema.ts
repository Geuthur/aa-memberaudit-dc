// AA Memberaudit Doctrine Checker
import type { components } from "@/Api/OpenApi";

export type UserData = components["schemas"]["UserData"];

export type CharacterSchema = components["schemas"]["CharacterSchema"];
export type CharacterDoctrines = components["schemas"]["CharacterDoctrines"];
export type CorporationDoctrines = components["schemas"]["CorporationDoctrines"];
export type CorporationMemberOverview = components["schemas"]["CorporationMemberOverview"];
export type ActiveDoctrineOverview = components["schemas"]["ActiveDoctrineOverview"];
export type CorporationMembersResponse = components["schemas"]["CorporationMembersResponse"];
export type AuditMembersRequest = components["schemas"]["AuditMembersRequest"];
export type CharacterOverviewSchema = components["schemas"]["CharacterOverviewSchema"];
export type CorporationOverviewSchema = components["schemas"]["CorporationOverviewSchema"];
export type MissingSkillsResponse = components["schemas"]["MissingSkillsResponse"];
export type MissingSkillDetail = components["schemas"]["MissingSkillDetail"];
export type DoctrineDetailResponse = components["schemas"]["DoctrineDetailResponse"];
export type ManageSkillListSchema = components["schemas"]["ManageSkillListSchema"];
export type SkillListUpdateRequest = components["schemas"]["SkillListUpdateRequest"];
export type Message = components["schemas"]["Message"];
export type SkillListCreateRequest = components["schemas"]["SkillListCreateRequest"];
