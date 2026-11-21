// Third Party
import { apiErrorMessage } from "aa-geuthur-react";

// AA Memberaudit Doctrine Checker
import { apiClient } from "@/Api/Api";
import type {
  CorporationDoctrines,
  CorporationMembersResponse,
} from "@/Api/schema";

/** Query keys of the corporation area. */
export const corporationQueryKeys = {
  doctrines: (corporationId: number) =>
    ["CorporationDoctrines", corporationId] as const,
  members: (corporationId: number) =>
    ["CorporationMembers", corporationId] as const,
};

export async function loadCorporationDoctrines(
  corporationId: number,
  category?: string,
  doctrineIds?: number[]
): Promise<CorporationDoctrines[]> {
  const { data, error } = await apiClient.GET(
    "/madc/api/{corporation_id}/doctrines/view/corporation/",
    {
      params: {
        path: { corporation_id: corporationId },
        query: {
          category: category,
          doctrine_ids: doctrineIds,
        },
      },
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, `Failed to load corporation doctrines for corporation ${corporationId}`));
  }
  return data;
}

export async function loadCorporationMembers(
  corporationId: number
): Promise<CorporationMembersResponse> {
  const { data, error } = await apiClient.GET(
    "/madc/api/{corporation_id}/doctrines/members/",
    {
      params: {
        path: { corporation_id: corporationId },
      },
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, `Failed to load members for corporation ${corporationId}`));
  }
  return data;
}

export async function auditCorporationMembers(
  corporationId: number,
  characterIds?: number[],
  category?: string,
  doctrineIds?: number[]
): Promise<CorporationDoctrines[]> {
  const { data, error } = await apiClient.POST(
    "/madc/api/{corporation_id}/doctrines/audit-members/",
    {
      params: {
        path: { corporation_id: corporationId },
      },
      body: {
        character_ids: characterIds,
        category: category,
        doctrine_ids: doctrineIds,
      },
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, `Failed to audit members for corporation ${corporationId}`));
  }
  return data;
}
