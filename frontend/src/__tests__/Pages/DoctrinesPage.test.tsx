// React
import { MemoryRouter } from "react-router-dom";

// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useUserData } from "aa-geuthur-react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA Memberaudit Doctrine Checker
import * as doctrinesCalls from "@/Api/calls/doctrines";
import DoctrinesPage from "@/Pages/DoctrinesPage";

vi.mock("@/Api/calls/doctrines", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/Api/calls/doctrines")>()),
  loadDoctrines: vi.fn(),
  loadMissingSkills: vi.fn(),
  loadDoctrineSkills: vi.fn(),
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
      <MemoryRouter initialEntries={["/madc/"]}>
        <DoctrinesPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe("DoctrinesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render character info and doctrine list grouped by category", async () => {
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

    vi.mocked(doctrinesCalls.loadDoctrines).mockResolvedValue([
      {
        character: {
          character_id: 99001,
          character_name: "Test Pilot",
          corporation_id: 98001,
          corporation_name: "Test Corp",
          alliance_id: null,
          alliance_name: null,
          character_icon: null,
        },
        doctrines: {
          "Cerberus Fleet": {
            id: 1,
            name: "Cerberus Fleet",
            category: "Cruiser",
            order: 1,
            skills: [],
          },
          "Eagle Fleet": {
            id: 2,
            name: "Eagle Fleet",
            category: "Cruiser",
            order: 2,
            skills: [{ skill_name: "Caldari Cruiser", required_level: 5 }],
          },
        },
      },
    ]);

    // Test Action
    renderPage();

    // Expected Result
    expect(await screen.findByText("Test Pilot")).toBeTruthy();
    expect(screen.getByText("Cruiser")).toBeTruthy();
    expect(screen.getByText("Cerberus Fleet")).toBeTruthy();
    expect(screen.getByText("Eagle Fleet")).toBeTruthy();
    expect(screen.getByText("Ready")).toBeTruthy();
    expect(screen.getByText("1 Missing")).toBeTruthy();
  });

  it("should render character selection buttons with aa-btn classes and switch character on click", async () => {
    // Test Data
    const user = userEvent.setup();
    vi.mocked(useUserData).mockReturnValue({
      data: {
      user: {
        user_id: 1,
        character_id: 99001,
        character_name: "Pilot Alpha",
        corporation_id: 98001,
        corporation_name: "Alpha Corp",
        alliance_id: null,
        alliance_name: null,
        portrait: null,
        is_admin: false,
        permissions: {},
      },
    },
    } as unknown as ReturnType<typeof useUserData>);

    vi.mocked(doctrinesCalls.loadDoctrines).mockResolvedValue([
      {
        character: {
          character_id: 99001,
          character_name: "Pilot Alpha",
          corporation_id: 98001,
          corporation_name: "Alpha Corp",
          alliance_id: null,
          alliance_name: null,
          character_icon: null,
        },
        doctrines: {
          "Alpha Shield": {
            id: 11,
            name: "Alpha Shield",
            category: "Battleship",
            order: 1,
            skills: [],
          },
        },
      },
      {
        character: {
          character_id: 99002,
          character_name: "Pilot Beta",
          corporation_id: 98001,
          corporation_name: "Alpha Corp",
          alliance_id: null,
          alliance_name: null,
          character_icon: null,
        },
        doctrines: {
          "Beta Armor": {
            id: 12,
            name: "Beta Armor",
            category: "Cruiser",
            order: 1,
            skills: [],
          },
        },
      },
    ]);

    // Test Action
    renderPage();

    // Expected Result
    const alphaButton = await screen.findByRole("button", { name: /pilot alpha/i });
    const betaButton = screen.getByRole("button", { name: /pilot beta/i });

    expect(alphaButton).toHaveClass("aa-btn", "aa-btn-primary");
    expect(betaButton).toHaveClass("aa-btn", "aa-btn-secondary");
    expect(screen.getByText("Alpha Shield")).toBeTruthy();

    // Switch to Pilot Beta
    await user.click(betaButton);

    expect(alphaButton).toHaveClass("aa-btn", "aa-btn-secondary");
    expect(betaButton).toHaveClass("aa-btn", "aa-btn-primary");
    expect(screen.getByText("Beta Armor")).toBeTruthy();
  });
});
