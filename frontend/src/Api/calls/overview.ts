// Third Party
import { apiErrorMessage } from "aa-geuthur-react";

// AA Memberaudit Doctrine Checker
import { apiClient } from "@/Api/Api";
import type {
  CharacterOverviewSchema,
  CorporationOverviewSchema,
} from "@/Api/schema";

/** Query keys of the overview area. */
export const overviewQueryKeys = {
  account: ["AccountOverview"] as const,
  corporation: ["CorporationOverview"] as const,
};

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
