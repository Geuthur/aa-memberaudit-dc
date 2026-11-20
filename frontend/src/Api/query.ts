// Third Party
import { queryKeys as baseQueryKeys } from "aa-geuthur-react";

export const queryKeys = {
  ...baseQueryKeys,
  Doctrines: (characterId: number) => ["Doctrines", characterId] as const,
  CorporationDoctrines: (corporationId: number) =>
    ["CorporationDoctrines", corporationId] as const,
  CorporationMembers: (corporationId: number) =>
    ["CorporationMembers", corporationId] as const,
  AccountOverview: ["AccountOverview"] as const,
  CorporationOverview: ["CorporationOverview"] as const,
  MissingSkills: (characterId: number, doctrineId: number) =>
    ["MissingSkills", characterId, doctrineId] as const,
  DoctrineSkills: (doctrineId: number, characterId?: number | null) =>
    ["DoctrineSkills", doctrineId, characterId ?? 0] as const,
  ManageDoctrines: ["ManageDoctrines"] as const,
};
