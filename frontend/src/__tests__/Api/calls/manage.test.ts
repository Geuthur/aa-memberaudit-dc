// Third Party
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA Memberaudit Doctrine Checker
import { apiClient } from "@/Api/Api";
import {
  createSkillList,
  deleteSkillList,
  loadManageDoctrines,
  manageMutationKeys,
  manageQueryKeys,
  updateSkillList,
} from "@/Api/calls/manage";

describe("manage keys", () => {
  it("provides the query and mutation keys", () => {
    expect(manageQueryKeys.skillLists).toEqual(["ManageDoctrines"]);
    expect(manageMutationKeys.updateSkillList).toEqual(["UpdateSkillList"]);
    expect(manageMutationKeys.deleteSkillList).toEqual(["DeleteSkillList"]);
  });
});

describe("Manage API calls", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("loadManageDoctrines", () => {
    it("fetches manage doctrines list", async () => {
      // Test Data
      const mockList = [
        {
          id: 1,
          name: "Test Doctrine",
          category: "Cruiser",
          ordering: 1,
          active: true,
          skill_count: 5,
        },
      ];
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: mockList,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadManageDoctrines();

      // Expected Result
      expect(result).toEqual(mockList);
      expect(apiClient.GET).toHaveBeenCalledWith(
        "/madc/api/manage/"
      );
    });
  });

  describe("updateSkillList", () => {
    it("passes the id as path parameter and the changes as body", async () => {
      // Test Data
      const mockSkillList = { id: 3, name: "Doctrine" };
      vi.spyOn(apiClient, "PUT").mockResolvedValueOnce({
        data: mockSkillList,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await updateSkillList(3, { name: "Doctrine" });

      // Expected Result
      expect(result).toEqual(mockSkillList);
      expect(apiClient.PUT).toHaveBeenCalledWith("/madc/api/manage/skilllist/{pk}/", {
        params: { path: { pk: 3 } },
        body: { name: "Doctrine" },
      });
    });
  });
});

type Method = "GET" | "POST" | "PUT" | "DELETE";

/** Every call of `calls/manage.ts`: [name, HTTP method, call, fixed text]. */
const calls: [string, Method, () => Promise<unknown>, string][] = [
  ["loadManageDoctrines", "GET", () => loadManageDoctrines(), "Failed to load skill lists for management"],
  [
    "createSkillList",
    "POST",
    () => createSkillList({ name: "Doctrine", category: null, ordering: 1, skill_list: "Mining 1" }),
    "Failed to create skill list",
  ],
  ["updateSkillList", "PUT", () => updateSkillList(3, { name: "Doctrine" }), "Failed to update skill list 3"],
  ["deleteSkillList", "DELETE", () => deleteSkillList(3), "Failed to delete skill list 3"],
];

const failWith = (method: Method, error: unknown) =>
  vi.spyOn(apiClient, method).mockResolvedValueOnce({
    data: undefined,
    error,
    response: new Response(),
  } as never);

describe("Manage API call errors", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe.each(calls)("%s", (_name, method, call, fixedText) => {
    it("should throw the message of the API when the request fails", async () => {
      // Test Data
      failWith(method, { error: "Permission Denied" });

      // Test Action & Expected Result
      await expect(call()).rejects.toThrow("Permission Denied");
    });

    it("should throw the fixed text when the API sent no message", async () => {
      // Test Data
      failWith(method, {});

      // Test Action & Expected Result
      await expect(call()).rejects.toThrow(fixedText);
    });
  });
});
