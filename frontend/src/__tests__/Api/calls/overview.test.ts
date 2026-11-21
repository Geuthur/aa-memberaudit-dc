// Third Party
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA Memberaudit Doctrine Checker
import { apiClient } from "@/Api/Api";
import {
  loadAccountOverview,
  loadCorporationOverview,
  overviewQueryKeys,
} from "@/Api/calls/overview";

describe("overviewQueryKeys", () => {
  it("provides the overview keys", () => {
    expect(overviewQueryKeys.account).toEqual(["AccountOverview"]);
    expect(overviewQueryKeys.corporation).toEqual(["CorporationOverview"]);
  });
});

describe("Overview API calls", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("loadAccountOverview", () => {
    it("fetches the account overview", async () => {
      // Test Data
      const mockList = [{ character_id: 42 }];
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: mockList,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadAccountOverview();

      // Expected Result
      expect(result).toEqual(mockList);
      expect(apiClient.GET).toHaveBeenCalledWith("/madc/api/account/overview/");
    });
  });

  describe("loadCorporationOverview", () => {
    it("fetches the corporation overview", async () => {
      // Test Data
      const mockList = [{ corporation_id: 7 }];
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: mockList,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadCorporationOverview();

      // Expected Result
      expect(result).toEqual(mockList);
      expect(apiClient.GET).toHaveBeenCalledWith("/madc/api/corporation/overview/");
    });
  });
});

type Method = "GET" | "POST" | "PUT" | "DELETE";

/** Every call of `calls/overview.ts`: [name, HTTP method, call, fixed text]. */
const calls: [string, Method, () => Promise<unknown>, string][] = [
  ["loadAccountOverview", "GET", () => loadAccountOverview(), "Failed to load account overview"],
  ["loadCorporationOverview", "GET", () => loadCorporationOverview(), "Failed to load corporation overview"],
];

const failWith = (method: Method, error: unknown) =>
  vi.spyOn(apiClient, method).mockResolvedValueOnce({
    data: undefined,
    error,
    response: new Response(),
  } as never);

describe("Overview API call errors", () => {
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
