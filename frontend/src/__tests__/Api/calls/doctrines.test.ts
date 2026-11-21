// Third Party
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA Memberaudit Doctrine Checker
import { apiClient } from "@/Api/Api";
import {
  doctrinesQueryKeys,
  loadDoctrineSkills,
  loadDoctrines,
  loadMissingSkills,
} from "@/Api/calls/doctrines";

describe("doctrinesQueryKeys", () => {
  it("provides the doctrine keys", () => {
    expect(doctrinesQueryKeys.doctrines(42)).toEqual(["Doctrines", 42]);
    expect(doctrinesQueryKeys.missingSkills(42, 3)).toEqual(["MissingSkills", 42, 3]);
    expect(doctrinesQueryKeys.doctrineSkills(3)).toEqual(["DoctrineSkills", 3, 0]);
    expect(doctrinesQueryKeys.doctrineSkills(3, 42)).toEqual(["DoctrineSkills", 3, 42]);
  });
});

describe("Doctrines API calls", () => {
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

  describe("loadMissingSkills", () => {
    it("passes character and doctrine id as path parameters", async () => {
      // Test Data
      const mockResponse = { missing: [] };
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: mockResponse,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadMissingSkills(42, 3);

      // Expected Result
      expect(result).toEqual(mockResponse);
      expect(apiClient.GET).toHaveBeenCalledWith(
        "/madc/api/{character_id}/doctrines/{pk}/",
        { params: { path: { character_id: 42, pk: 3 } } }
      );
    });
  });

  describe("loadDoctrineSkills", () => {
    it("passes the character id as query parameter", async () => {
      // Test Data
      const mockResponse = { skills: [] };
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: mockResponse,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadDoctrineSkills(3, 42);

      // Expected Result
      expect(result).toEqual(mockResponse);
      expect(apiClient.GET).toHaveBeenCalledWith("/madc/api/doctrines/{pk}/", {
        params: { path: { pk: 3 }, query: { character_id: 42 } },
      });
    });

    it("sends no query without a character id", async () => {
      // Test Data
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: { skills: [] },
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      await loadDoctrineSkills(3, null);

      // Expected Result
      expect(apiClient.GET).toHaveBeenCalledWith("/madc/api/doctrines/{pk}/", {
        params: { path: { pk: 3 }, query: undefined },
      });
    });
  });
});

type Method = "GET" | "POST" | "PUT" | "DELETE";

/** Every call of `calls/doctrines.ts`: [name, HTTP method, call, fixed text]. */
const calls: [string, Method, () => Promise<unknown>, string][] = [
  ["loadDoctrines", "GET", () => loadDoctrines(42), "Failed to load doctrines for character 42"],
  ["loadMissingSkills", "GET", () => loadMissingSkills(42, 3), "Failed to load missing skills"],
  ["loadDoctrineSkills", "GET", () => loadDoctrineSkills(3), "Failed to load doctrine skills"],
];

const failWith = (method: Method, error: unknown) =>
  vi.spyOn(apiClient, method).mockResolvedValueOnce({
    data: undefined,
    error,
    response: new Response(),
  } as never);

describe("Doctrines API call errors", () => {
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
