// React
import { MemoryRouter } from "react-router-dom";

// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { useUserData } from "aa-geuthur-react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA Memberaudit Doctrine Checker
import * as ApiCalls from "@/Api/ApiCalls";
import CorporationDoctrinesPage from "@/Pages/CorporationDoctrinesPage";

vi.mock("@/Api/ApiCalls", () => ({
  loadCorporationMembers: vi.fn(),
  auditCorporationMembers: vi.fn(),
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
      <MemoryRouter initialEntries={["/madc/corporation/"]}>
        <CorporationDoctrinesPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

const mockCorpMembers = [
  {
    character: {
      character_id: 99001,
      character_name: "Fleet Commander",
      corporation_id: 98001,
      corporation_name: "Test Corp",
      alliance_id: null,
      alliance_name: null,
      character_icon: null,
    },
    alts: [
      {
        character_id: 99002,
        character_name: "FC Alt",
        corporation_id: 98001,
        corporation_name: "Test Corp",
        alliance_id: null,
        alliance_name: null,
        character_icon: null,
      },
    ],
    doctrines: {
      "Cerberus Fleet": {
        id: 10,
        name: "Cerberus Fleet",
        category: "Cruiser",
        order: 1,
        skills: [],
      },
      "Eagle Fleet": {
        id: 11,
        name: "Eagle Fleet",
        category: "Cruiser",
        order: 2,
        skills: [{ skill_name: "Caldari Cruiser", required_level: 5 }],
      },
    },
  },
  {
    character: {
      character_id: 99003,
      character_name: "Rookie Pilot",
      corporation_id: 98001,
      corporation_name: "Test Corp",
      alliance_id: null,
      alliance_name: null,
      character_icon: null,
    },
    alts: [],
    doctrines: {
      "Cerberus Fleet": {
        id: 10,
        name: "Cerberus Fleet",
        category: "Cruiser",
        order: 1,
        skills: [{ skill_name: "Heavy Missile Specialization", required_level: 4 }],
      },
    },
  },
];

const mockMembersResponse = {
  corporation_id: 98001,
  corporation_name: "Test Corp",
  members: [
    {
      character: mockCorpMembers[0].character,
      alts: mockCorpMembers[0].alts,
    },
    {
      character: mockCorpMembers[1].character,
      alts: mockCorpMembers[1].alts,
    },
  ],
  doctrines: [
    { id: 10, name: "Cerberus Fleet", category: "Cruiser", order: 1 },
    { id: 11, name: "Eagle Fleet", category: "Cruiser", order: 2 },
  ],
};

describe("CorporationDoctrinesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render members with Ready and Not Ready badges in default Badges view", async () => {
    // Test Data
    vi.mocked(useUserData).mockReturnValue({
      data: {
      user: {
        user_id: 1,
        character_id: 99001,
        character_name: "Fleet Commander",
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

    vi.mocked(ApiCalls.loadCorporationMembers).mockResolvedValue(mockMembersResponse);
    vi.mocked(ApiCalls.auditCorporationMembers).mockResolvedValue(mockCorpMembers);

    // Test Action
    renderPage();

    // Expected Result
    expect(await screen.findByText("Fleet Commander")).toBeTruthy();
    expect(screen.getByText("+1 alts")).toBeTruthy();
    expect(screen.getByText("Rookie Pilot")).toBeTruthy();

    // Verify Ready and Not Ready badges after progressive audit
    const notReadyBadges = await screen.findAllByText(/Not Ready \(1\)/);
    expect(notReadyBadges.length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Ready/).length).toBeGreaterThan(0);
  });

  it("should toggle to Matrix view and show Ready and Not Ready badges in table cells", async () => {
    // Test Data
    vi.mocked(useUserData).mockReturnValue({
      data: {
      user: {
        user_id: 1,
        character_id: 99001,
        character_name: "Fleet Commander",
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

    vi.mocked(ApiCalls.loadCorporationMembers).mockResolvedValue(mockMembersResponse);
    vi.mocked(ApiCalls.auditCorporationMembers).mockResolvedValue(mockCorpMembers);

    // Test Action
    renderPage();
    await screen.findByText("Fleet Commander");
    await screen.findAllByText(/Not Ready \(1\)/);

    const matrixButton = screen.getByTitle("Matrix View");
    fireEvent.click(matrixButton);

    // Expected Result
    expect(screen.getByText("Cerberus Fleet")).toBeTruthy();
    expect(screen.getByText("Eagle Fleet")).toBeTruthy();
    expect(screen.getAllByText("Ready").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Not Ready").length).toBeGreaterThan(0);

    // Verify sticky header and sticky first column on Matrix BaseTable
    const table = document.querySelector("table.aa-table");
    expect(table?.classList.contains("aa-table-sticky-header")).toBe(true);
    expect(table?.classList.contains("aa-table-sticky-first-col")).toBe(true);

    // The shell class lets the app CSS give the scroll area its maximum height
    expect(document.querySelector(".madc-matrix .aa-table-scroll")).not.toBeNull();
  });

  it("should filter members when searching by character name", async () => {
    // Test Data
    vi.mocked(useUserData).mockReturnValue({
      data: {
      user: {
        user_id: 1,
        character_id: 99001,
        character_name: "Fleet Commander",
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

    vi.mocked(ApiCalls.loadCorporationMembers).mockResolvedValue(mockMembersResponse);
    vi.mocked(ApiCalls.auditCorporationMembers).mockResolvedValue(mockCorpMembers);

    // Test Action
    renderPage();
    await screen.findByText("Fleet Commander");

    const searchInput = screen.getByPlaceholderText("Filter by character or alt name...");
    fireEvent.change(searchInput, { target: { value: "Rookie" } });

    // Expected Result
    expect(screen.getByText("Rookie Pilot")).toBeTruthy();
    expect(screen.queryByText("Fleet Commander")).toBeNull();
  });

  it("should display correct corporation name when viewing a specific corporation from route", async () => {
    // Test Data
    vi.mocked(useUserData).mockReturnValue({
      data: {
      user: {
        user_id: 1,
        character_id: 99001,
        character_name: "Fleet Commander",
        corporation_id: 98001,
        corporation_name: "User Own Corp",
        alliance_id: null,
        alliance_name: null,
        portrait: null,
        is_admin: false,
        permissions: {},
      },
    },
    } as unknown as ReturnType<typeof useUserData>);

    vi.mocked(ApiCalls.loadCorporationMembers).mockResolvedValue({
      ...mockMembersResponse,
      corporation_id: 98002,
      corporation_name: "Target Selected Corp",
    });
    vi.mocked(ApiCalls.auditCorporationMembers).mockResolvedValue([]);

    // Test Action
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    });
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/madc/corporation/98002/"]}>
          <CorporationDoctrinesPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    // Expected Result
    await screen.findByText("Target Selected Corp");
    expect(screen.getByText("Target Selected Corp")).toBeTruthy();
    expect(screen.queryByText("User Own Corp")).toBeNull();
  });

  it("should render view mode and status filter button groups with aa-btn classes", async () => {
    // Test Data
    vi.mocked(useUserData).mockReturnValue({
      data: {
      user: {
        user_id: 1,
        character_id: 99001,
        character_name: "Fleet Commander",
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

    vi.mocked(ApiCalls.loadCorporationMembers).mockResolvedValue(mockMembersResponse);
    vi.mocked(ApiCalls.auditCorporationMembers).mockResolvedValue([]);

    // Test Action
    renderPage();
    await screen.findByText("Fleet Commander");

    // Expected Result
    const badgesBtn = screen.getByTitle("Badges View");
    const matrixBtn = screen.getByTitle("Matrix View");
    expect(badgesBtn).toHaveClass("aa-btn", "aa-btn-primary");
    expect(matrixBtn).toHaveClass("aa-btn", "aa-btn-secondary");

    // Click Matrix View
    fireEvent.click(matrixBtn);
    expect(badgesBtn).toHaveClass("aa-btn", "aa-btn-secondary");
    expect(matrixBtn).toHaveClass("aa-btn", "aa-btn-primary");
  });

  it("should show doctrines without category under the Uncategorized filter", async () => {
    // Test Data: Eagle Fleet has no category
    vi.mocked(useUserData).mockReturnValue({
      data: {
        user: {
          user_id: 1,
          character_id: 99001,
          character_name: "Fleet Commander",
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
    vi.mocked(ApiCalls.loadCorporationMembers).mockResolvedValue({
      ...mockMembersResponse,
      doctrines: [
        { id: 10, name: "Cerberus Fleet", category: "Cruiser", order: 1 },
        { id: 11, name: "Eagle Fleet", category: "", order: 2 },
      ],
    });
    vi.mocked(ApiCalls.auditCorporationMembers).mockResolvedValue(mockCorpMembers);

    // Test Action
    renderPage();
    await screen.findByText("Fleet Commander");
    await screen.findAllByText(/Not Ready \(1\)/);
    fireEvent.click(screen.getByTitle("Matrix View"));
    fireEvent.change(screen.getByDisplayValue("All Categories"), {
      target: { value: "Uncategorized" },
    });

    // Expected Result
    expect(screen.getByText("Eagle Fleet")).toBeTruthy();
    expect(screen.queryByText("Cerberus Fleet")).toBeNull();
  });
});
