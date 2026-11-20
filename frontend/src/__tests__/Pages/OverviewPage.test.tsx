// React
import { MemoryRouter } from "react-router-dom";

// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { useUserData } from "aa-geuthur-react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA Memberaudit Doctrine Checker
import * as ApiCalls from "@/Api/ApiCalls";
import OverviewPage from "@/Pages/OverviewPage";

vi.mock("@/Api/ApiCalls", () => ({
  loadAccountOverview: vi.fn(),
  loadCorporationOverview: vi.fn(),
}));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key }),
  withTranslation: () => (Component: unknown) => Component,
}));

vi.mock("aa-geuthur-react", async (importOriginal) => ({
  ...(await importOriginal<typeof import("aa-geuthur-react")>()),
  useUserData: vi.fn(),
}));

const renderPage = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/madc/overview/"]}>
        <OverviewPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe("OverviewPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render account overview table with characters", async () => {
    // Test Data
    vi.mocked(useUserData).mockReturnValue({
      data: {
      user: {
        user_id: 1,
        character_id: 99001,
        character_name: "Test Pilot",
        corporation_id: 98001,
        corporation_name: "Test Corp",
        alliance_id: null,
        alliance_name: null,
        portrait: null,
        is_admin: false,
        permissions: {},
      },
    },
    } as unknown as ReturnType<typeof useUserData>);

    vi.mocked(ApiCalls.loadAccountOverview).mockResolvedValue([
      {
        character_id: 99001,
        character_name: "Test Pilot",
        corporation_id: 98001,
        corporation_name: "Test Corp",
        alliance_id: null,
        alliance_name: null,
        character_icon: null,
        actions: "/doctrine/99001/",
      },
    ]);

    // Test Action
    renderPage();

    // Expected Result
    expect(await screen.findByText("Test Pilot")).toBeTruthy();
    expect(screen.getByText("Test Corp")).toBeTruthy();
    const actionLink = screen.getByRole("link", { name: /view doctrines/i });
    expect(actionLink).toHaveClass("aa-btn", "aa-btn-sm", "aa-btn-primary");

    const accountBtn = screen.getByRole("button", { name: /account overview/i });
    expect(accountBtn).toHaveClass("aa-btn", "aa-btn-primary");
  });

  it("should render corporation overview tab with aa-btn classes and switch tab on click", async () => {
    // Test Data
    vi.mocked(useUserData).mockReturnValue({
      data: {
      user: {
        user_id: 1,
        character_id: 99001,
        character_name: "Test Pilot",
        corporation_id: 98001,
        corporation_name: "Test Corp",
        alliance_id: null,
        alliance_name: null,
        portrait: null,
        is_admin: true,
        permissions: { corp_access: true },
      },
    },
    } as unknown as ReturnType<typeof useUserData>);

    vi.mocked(ApiCalls.loadAccountOverview).mockResolvedValue([]);
    vi.mocked(ApiCalls.loadCorporationOverview).mockResolvedValue([
      {
        corporation_id: 98001,
        corporation_name: "Test Corporation",
        alliance_id: null,
        alliance_name: null,
        corporation_icon: null,
        actions: "/corporation/98001/",
      },
    ]);

    // Test Action
    renderPage();
    const accountBtn = await screen.findByRole("button", { name: /account overview/i });
    const corpBtn = await screen.findByRole("button", { name: /corporation overview/i });

    // Expected Result
    expect(accountBtn).toHaveClass("aa-btn", "aa-btn-primary");
    expect(corpBtn).toHaveClass("aa-btn", "aa-btn-secondary");

    // Click Corporation Overview
    fireEvent.click(corpBtn);
    expect(accountBtn).toHaveClass("aa-btn", "aa-btn-secondary");
    expect(corpBtn).toHaveClass("aa-btn", "aa-btn-primary");
    expect(await screen.findByText("Test Corporation")).toBeTruthy();
    const corpActionLink = screen.getByRole("link", { name: /view overview/i });
    expect(corpActionLink).toHaveClass("aa-btn", "aa-btn-sm", "aa-btn-primary");
  });

  it("should show the corporation overview tab with alliance_access only", async () => {
    // Test Data
    vi.mocked(useUserData).mockReturnValue({
      data: {
        user: {
          user_id: 1,
          character_id: 99001,
          character_name: "Test Pilot",
          corporation_id: 98001,
          corporation_name: "Test Corp",
          is_admin: false,
          permissions: { corp_access: false, alliance_access: true },
        },
      },
    } as unknown as ReturnType<typeof useUserData>);
    vi.mocked(ApiCalls.loadAccountOverview).mockResolvedValue([]);
    vi.mocked(ApiCalls.loadCorporationOverview).mockResolvedValue([]);

    // Test Action
    renderPage();

    // Expected Result
    expect(
      await screen.findByRole("button", { name: /corporation overview/i })
    ).toBeTruthy();
    expect(ApiCalls.loadCorporationOverview).toHaveBeenCalled();
  });
});
