// Third Party
import { apiErrorMessage } from "aa-geuthur-react";

// AA Memberaudit Doctrine Checker
import { apiClient } from "@/Api/Api";
import type {
  CharacterDoctrines,
  CharacterOverviewSchema,
  CorporationDoctrines,
  CorporationMembersResponse,
  CorporationOverviewSchema,
  SkillListCreateRequest,
  DoctrineDetailResponse,
  SkillListUpdateRequest,
  ManageSkillListSchema,
  Message,
  MissingSkillsResponse,
} from "@/Api/schema";

export async function loadDoctrines(
  characterId: number
): Promise<CharacterDoctrines[]> {
  const { data, error } = await apiClient.GET(
    "/madc/api/{character_id}/doctrines/",
    {
      params: {
        path: { character_id: characterId },
      },
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, `Failed to load doctrines for character ${characterId}`));
  }
  return data;
}

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

export async function loadAccountOverview(): Promise<CharacterOverviewSchema[]> {
  const { data, error } = await apiClient.GET(
    "/madc/api/account/overview/"
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load account overview"));
  }
  return data;
}

export async function loadCorporationOverview(): Promise<
  CorporationOverviewSchema[]
> {
  const { data, error } = await apiClient.GET(
    "/madc/api/corporation/overview/"
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load corporation overview"));
  }
  return data;
}

export async function loadMissingSkills(
  characterId: number,
  doctrineId: number
): Promise<MissingSkillsResponse> {
  const { data, error } = await apiClient.GET(
    "/madc/api/{character_id}/doctrines/{pk}/",
    {
      params: {
        path: { character_id: characterId, pk: doctrineId },
      },
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load missing skills"));
  }
  return data;
}

export async function loadDoctrineSkills(
  doctrineId: number,
  characterId?: number | null
): Promise<DoctrineDetailResponse> {
  const { data, error } = await apiClient.GET(
    "/madc/api/doctrines/{pk}/",
    {
      params: {
        path: { pk: doctrineId },
        query: characterId ? { character_id: characterId } : undefined,
      },
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load doctrine skills"));
  }
  return data;
}

export async function loadManageDoctrines(): Promise<ManageSkillListSchema[]> {
  const { data, error } = await apiClient.GET(
    "/madc/api/manage/"
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load skill lists for management"));
  }
  return data;
}

export async function createSkillList(
  payload: SkillListCreateRequest
): Promise<ManageSkillListSchema> {
  const { data, error } = await apiClient.POST(
    "/madc/api/manage/skilllist/",
    {
      body: payload,
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to create skill list"));
  }
  return data;
}

export async function updateSkillList(
  pk: number,
  payload: SkillListUpdateRequest
): Promise<ManageSkillListSchema> {
  const { data, error } = await apiClient.PUT(
    "/madc/api/manage/skilllist/{pk}/",
    {
      params: {
        path: { pk },
      },
      body: payload,
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, `Failed to update skill list ${pk}`));
  }
  return data;
}

export async function deleteSkillList(
  pk: number
): Promise<Message> {
  const { data, error } = await apiClient.DELETE(
    "/madc/api/manage/skilllist/{pk}/",
    {
      params: {
        path: { pk },
      },
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, `Failed to delete skill list ${pk}`));
  }
  return data;
}
