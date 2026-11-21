// React
import { MemoryRouter } from "react-router-dom";

// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA Memberaudit Doctrine Checker
import * as doctrinesCalls from "@/Api/calls/doctrines";
import DoctrineSkillsModal from "@/Components/Modals/DoctrineSkillsModal";

vi.mock("@/Api/calls/doctrines", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/Api/calls/doctrines")>()),
  loadDoctrineSkills: vi.fn(),
}));

vi.mock("react-i18next", () => ({
  withTranslation: () => (Component: unknown) => Component,
  useTranslation: () => ({
    t: (key: string, options?: Record<string, unknown>) => {
      if (!options) return key;
      let text = key;
      for (const [k, v] of Object.entries(options)) {
        text = text.replace(new RegExp(`{{${k}}}`, "g"), String(v));
      }
      return text;
    },
  }),
}));

const renderModal = (props: {
  doctrineId: number | null;
  characterId?: number | null;
  show: boolean;
  onHide: () => void;
}) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <DoctrineSkillsModal {...props} />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe("DoctrineSkillsModal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render doctrine skills table using BaseModal and BaseTable", async () => {
    // Test Data
    const onHide = vi.fn();
    vi.mocked(doctrinesCalls.loadDoctrineSkills).mockResolvedValue({
      id: 1,
      name: "Cerberus Fleet",
      category: "Cruiser",
      ordering: 1,
      active: true,
      skills: {
        "Caldari Cruiser": 5,
        "Heavy Missiles": 4,
      },
    });

    // Test Action
    renderModal({
      doctrineId: 1,
      show: true,
      onHide,
    });

    // Expected Result
    expect(await screen.findByText("Required Skills: Cerberus Fleet")).toBeTruthy();
    expect(screen.getByText("Caldari Cruiser")).toBeTruthy();
    expect(screen.getByText("Heavy Missiles")).toBeTruthy();
    expect(screen.getByText("5")).toBeTruthy();
    expect(screen.getByText("4")).toBeTruthy();

    const indicators = screen.getAllByTestId("skill-level-indicator");
    expect(indicators).toHaveLength(2);
  });

  it("should display empty notice when doctrine has no required skills", async () => {
    // Test Data
    vi.mocked(doctrinesCalls.loadDoctrineSkills).mockResolvedValue({
      id: 2,
      name: "Empty Doctrine",
      category: "Frigate",
      ordering: 2,
      active: true,
      skills: {},
    });

    // Test Action
    renderModal({
      doctrineId: 2,
      show: true,
      onHide: vi.fn(),
    });

    // Expected Result
    expect(
      await screen.findByText("No required skills defined for this doctrine.")
    ).toBeTruthy();
  });

  it("should call onHide when close button is clicked", async () => {
    // Test Data
    const onHide = vi.fn();
    vi.mocked(doctrinesCalls.loadDoctrineSkills).mockResolvedValue({
      id: 1,
      name: "Cerberus Fleet",
      category: "Cruiser",
      ordering: 1,
      active: true,
      skills: {},
    });

    // Test Action
    renderModal({
      doctrineId: 1,
      show: true,
      onHide,
    });

    await screen.findByText("Required Skills: Cerberus Fleet");
    const closeBtns = screen.getAllByRole("button", { name: "Close" });
    fireEvent.click(closeBtns[0]);

    // Expected Result
    expect(onHide).toHaveBeenCalled();
  });

  it("should render green trained skills and white missing skills when character context is provided", async () => {
    // Test Data
    vi.mocked(doctrinesCalls.loadDoctrineSkills).mockResolvedValue({
      id: 1,
      name: "Cerberus Fleet",
      category: "Cruiser",
      ordering: 1,
      active: true,
      skills: {
        "Caldari Cruiser": 5,
        "Heavy Missiles": 4,
      },
      character_skills: {
        "Caldari Cruiser": 3, // Needs 5, trained 3: levels 1-3 should be green (text-success), 4-5 white (text-white)
        "Heavy Missiles": 4,  // Needs 4, trained 4: levels 1-4 should be green (text-success), 5 dimmed
      },
    });

    // Test Action
    renderModal({
      doctrineId: 1,
      characterId: 12345,
      show: true,
      onHide: vi.fn(),
    });

    // Expected Result
    expect(await screen.findByText("Required Skills: Cerberus Fleet")).toBeTruthy();
    const indicators = screen.getAllByTestId("skill-level-indicator");
    expect(indicators).toHaveLength(2);

    // First indicator ("Caldari Cruiser"): 3 green, 2 white
    const caldariCruiserLevels = indicators[0].querySelectorAll("i");
    expect(caldariCruiserLevels).toHaveLength(5);
    expect(caldariCruiserLevels[0].className).toContain("text-success");
    expect(caldariCruiserLevels[1].className).toContain("text-success");
    expect(caldariCruiserLevels[2].className).toContain("text-success");
    expect(caldariCruiserLevels[3].className).toContain("text-white");
    expect(caldariCruiserLevels[4].className).toContain("text-white");

    // Second indicator ("Heavy Missiles"): 4 green, 1 dimmed
    const missileLevels = indicators[1].querySelectorAll("i");
    expect(missileLevels).toHaveLength(5);
    expect(missileLevels[0].className).toContain("text-success");
    expect(missileLevels[1].className).toContain("text-success");
    expect(missileLevels[2].className).toContain("text-success");
    expect(missileLevels[3].className).toContain("text-success");
    expect(missileLevels[4].className).toContain("opacity-25");
  });

  it("should paginate skills and allow page navigation when doctrine has many skills", async () => {
    // Test Data: 12 skills, default page size is 10
    const manySkills: Record<string, number> = {};
    for (let i = 1; i <= 12; i++) {
      manySkills[`Test Skill ${i.toString().padStart(2, "0")}`] = 3;
    }
    vi.mocked(doctrinesCalls.loadDoctrineSkills).mockResolvedValue({
      id: 5,
      name: "Capital Fleet",
      category: "Capital",
      ordering: 1,
      active: true,
      skills: manySkills,
    });

    // Test Action
    renderModal({
      doctrineId: 5,
      show: true,
      onHide: vi.fn(),
    });

    // Expected Result: page 1 shows first 10 skills
    expect(await screen.findByText("Required Skills: Capital Fleet")).toBeTruthy();
    expect(screen.getByText("Test Skill 01")).toBeTruthy();
    expect(screen.getByText("Test Skill 10")).toBeTruthy();
    expect(screen.queryByText("Test Skill 11")).toBeNull();

    // Verify pagination controls: page 1 of 2
    expect(screen.getAllByText("Page 1 of 2").length).toBeGreaterThan(0);

    // Navigate to page 2 via next page button
    const nextBtn = screen.getByTitle("Next Page");
    fireEvent.click(nextBtn);

    // Expected Result: page 2 shows remaining skills
    expect(screen.getByText("Test Skill 11")).toBeTruthy();
    expect(screen.getByText("Test Skill 12")).toBeTruthy();
    expect(screen.queryByText("Test Skill 01")).toBeNull();
  });

  it("should filter skills by name when search text is entered", async () => {
    // Test Data: 8 skills
    const skillsList: Record<string, number> = {
      "Caldari Cruiser": 5,
      "Heavy Missiles": 4,
      "Shield Management": 4,
      "Shield Operation": 4,
      "Target Painting": 3,
      "Missile Projection": 4,
    };
    vi.mocked(doctrinesCalls.loadDoctrineSkills).mockResolvedValue({
      id: 6,
      name: "Search Test Fleet",
      category: "Cruiser",
      ordering: 1,
      active: true,
      skills: skillsList,
    });

    // Test Action
    renderModal({
      doctrineId: 6,
      show: true,
      onHide: vi.fn(),
    });

    expect(await screen.findByText("Required Skills: Search Test Fleet")).toBeTruthy();
    expect(screen.getByText("Caldari Cruiser")).toBeTruthy();
    expect(screen.getByText("Shield Management")).toBeTruthy();

    // Enter search filter "Shield"
    const searchInput = screen.getByPlaceholderText("Filter skills...");
    fireEvent.change(searchInput, { target: { value: "Shield" } });

    // Expected Result: only Shield skills are visible
    expect(screen.getByText("Shield Management")).toBeTruthy();
    expect(screen.getByText("Shield Operation")).toBeTruthy();
    expect(screen.queryByText("Caldari Cruiser")).toBeNull();
  });
});
