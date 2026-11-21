// Third Party
import { apiErrorMessage } from "aa-geuthur-react";

// AA Memberaudit Doctrine Checker
import { apiClient } from "@/Api/Api";
import type {
  CharacterDoctrines,
  DoctrineDetailResponse,
  MissingSkillsResponse,
} from "@/Api/schema";

/** Query keys of the doctrines area. */
export const doctrinesQueryKeys = {
  doctrines: (characterId: number) => ["Doctrines", characterId] as const,
  missingSkills: (characterId: number, doctrineId: number) =>
    ["MissingSkills", characterId, doctrineId] as const,
  doctrineSkills: (doctrineId: number, characterId?: number | null) =>
    ["DoctrineSkills", doctrineId, characterId ?? 0] as const,
};

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
