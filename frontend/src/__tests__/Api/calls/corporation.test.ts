// Third Party
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA Memberaudit Doctrine Checker
import { apiClient } from "@/Api/Api";
import {
  auditCorporationMembers,
  corporationQueryKeys,
  loadCorporationDoctrines,
  loadCorporationMembers,
} from "@/Api/calls/corporation";

describe("corporationQueryKeys", () => {
  it("provides the corporation keys", () => {
    expect(corporationQueryKeys.doctrines(7)).toEqual(["CorporationDoctrines", 7]);
    expect(corporationQueryKeys.members(7)).toEqual(["CorporationMembers", 7]);
  });
});

describe("Corporation API calls", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("loadCorporationDoctrines", () => {
    it("passes the filters as query parameters", async () => {
      // Test Data
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: [],
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadCorporationDoctrines(7, "Cruiser", [1, 2]);

      // Expected Result
      expect(result).toEqual([]);
      expect(apiClient.GET).toHaveBeenCalledWith(
        "/madc/api/{corporation_id}/doctrines/view/corporation/",
        {
          params: {
            path: { corporation_id: 7 },
            query: { category: "Cruiser", doctrine_ids: [1, 2] },
          },
        }
      );
    });
  });

  describe("loadCorporationMembers", () => {
    it("passes the corporation id as path parameter", async () => {
      // Test Data
      const mockResponse = { members: [] };
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: mockResponse,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadCorporationMembers(7);

      // Expected Result
      expect(result).toEqual(mockResponse);
      expect(apiClient.GET).toHaveBeenCalledWith(
        "/madc/api/{corporation_id}/doctrines/members/",
        { params: { path: { corporation_id: 7 } } }
      );
    });
  });

  describe("auditCorporationMembers", () => {
    it("sends the characters and filters in the body", async () => {
      // Test Data
      vi.spyOn(apiClient, "POST").mockResolvedValueOnce({
        data: [],
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      await auditCorporationMembers(7, [42], "Cruiser", [1]);

      // Expected Result
      expect(apiClient.POST).toHaveBeenCalledWith(
        "/madc/api/{corporation_id}/doctrines/audit-members/",
        {
          params: { path: { corporation_id: 7 } },
          body: { character_ids: [42], category: "Cruiser", doctrine_ids: [1] },
        }
      );
    });
  });
});

type Method = "GET" | "POST" | "PUT" | "DELETE";

/** Every call of `calls/corporation.ts`: [name, HTTP method, call, fixed text]. */
const calls: [string, Method, () => Promise<unknown>, string][] = [
  [
    "loadCorporationDoctrines",
    "GET",
    () => loadCorporationDoctrines(7),
    "Failed to load corporation doctrines for corporation 7",
  ],
  ["loadCorporationMembers", "GET", () => loadCorporationMembers(7), "Failed to load members for corporation 7"],
  ["auditCorporationMembers", "POST", () => auditCorporationMembers(7), "Failed to audit members for corporation 7"],
];

const failWith = (method: Method, error: unknown) =>
  vi.spyOn(apiClient, method).mockResolvedValueOnce({
    data: undefined,
    error,
    response: new Response(),
  } as never);

describe("Corporation API call errors", () => {
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
