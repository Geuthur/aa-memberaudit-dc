// Third Party
import { apiErrorMessage } from "aa-geuthur-react";

// AA Memberaudit Doctrine Checker
import { apiClient } from "@/Api/Api";
import type {
  SkillListCreateRequest,
  SkillListUpdateRequest,
  ManageSkillListSchema,
  Message,
} from "@/Api/schema";

/** Query keys of the manage area. */
export const manageQueryKeys = {
  skillLists: ["ManageDoctrines"] as const,
};

/** Mutation keys of the manage area. */
export const manageMutationKeys = {
  updateSkillList: ["UpdateSkillList"] as const,
  deleteSkillList: ["DeleteSkillList"] as const,
};

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
