// Third Party
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA Memberaudit Doctrine Checker
import { apiClient } from "@/Api/Api";
import {
  auditCorporationMembers,
  createSkillList,
  deleteSkillList,
  loadAccountOverview,
  loadCorporationDoctrines,
  loadCorporationMembers,
  loadCorporationOverview,
  loadDoctrines,
  loadDoctrineSkills,
  loadManageDoctrines,
  loadMissingSkills,
  updateSkillList,
} from "@/Api/ApiCalls";

describe("General API client functions", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("loadDoctrines", () => {
    it("fetches doctrines for character", async () => {
      // Test Data
      const mockDoctrines = [
        {
          character: {
            character_id: 42,
            character_name: "Test",
            corporation_id: 1,
            corporation_name: "Corp",
          },
          doctrines: {},
        },
      ];
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: mockDoctrines,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadDoctrines(42);

      // Expected Result
      expect(result).toEqual(mockDoctrines);
      expect(apiClient.GET).toHaveBeenCalledWith(
        "/madc/api/{character_id}/doctrines/",
        {
          params: { path: { character_id: 42 } },
        }
      );
    });

    it("fetches doctrines with targetCharacterId and allCharacters", async () => {
      // Test Data
      const mockDoctrines = [
        {
          character: {
            character_id: 42,
            character_name: "Test",
            corporation_id: 1,
            corporation_name: "Corp",
          },
          doctrines: {},
        },
      ];
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: mockDoctrines,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadDoctrines(42);

      // Expected Result
      expect(result).toEqual(mockDoctrines);
      expect(apiClient.GET).toHaveBeenCalledWith(
        "/madc/api/{character_id}/doctrines/",
        {
          params: {
            path: { character_id: 42 },
          },
        }
      );
    });
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
});

type Method = "GET" | "POST" | "PUT" | "DELETE";

/** Every call of `ApiCalls.ts`: [name, HTTP method, call, fixed text]. */
const calls: [string, Method, () => Promise<unknown>, string][] = [
  ["loadDoctrines", "GET", () => loadDoctrines(42), "Failed to load doctrines for character 42"],
  [
    "loadCorporationDoctrines",
    "GET",
    () => loadCorporationDoctrines(7),
    "Failed to load corporation doctrines for corporation 7",
  ],
  ["loadCorporationMembers", "GET", () => loadCorporationMembers(7), "Failed to load members for corporation 7"],
  ["auditCorporationMembers", "POST", () => auditCorporationMembers(7), "Failed to audit members for corporation 7"],
  ["loadAccountOverview", "GET", () => loadAccountOverview(), "Failed to load account overview"],
  ["loadCorporationOverview", "GET", () => loadCorporationOverview(), "Failed to load corporation overview"],
  ["loadMissingSkills", "GET", () => loadMissingSkills(42, 3), "Failed to load missing skills"],
  ["loadDoctrineSkills", "GET", () => loadDoctrineSkills(3), "Failed to load doctrine skills"],
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

describe("API call errors", () => {
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
