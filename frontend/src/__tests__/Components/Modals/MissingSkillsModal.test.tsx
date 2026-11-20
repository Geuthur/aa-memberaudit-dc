// React
import { MemoryRouter } from "react-router-dom";

// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA Memberaudit Doctrine Checker
import * as ApiCalls from "@/Api/ApiCalls";
import MissingSkillsModal from "@/Components/Modals/MissingSkillsModal";

vi.mock("@/Api/ApiCalls", () => ({
  loadMissingSkills: vi.fn(),
}));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key }),
  withTranslation: () => (Component: unknown) => Component,
}));

const renderModal = (props: {
  characterId: number | null;
  doctrineId: number | null;
  show: boolean;
  onHide: () => void;
}) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <MissingSkillsModal {...props} />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe("MissingSkillsModal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render missing skills table using BaseModal and BaseTable when data is loaded", async () => {
    // Test Data
    const onHide = vi.fn();
    vi.mocked(ApiCalls.loadMissingSkills).mockResolvedValue({
      character_id: 99001,
      character_name: "Fleet Commander",
      doctrine_id: 1,
      doctrine_name: "Cerberus Fleet",
      missing_skills: [
        {
          name: "Heavy Missile Specialization",
          trained_level: 2,
          needed_level: 4,
        },
      ],
      clipboard_export: "Heavy Missile Specialization 4",
    });

    // Test Action
    renderModal({
      characterId: 99001,
      doctrineId: 1,
      show: true,
      onHide,
    });

    // Expected Result: modal title and skill table content rendered
    expect(
      await screen.findByText("Missing Skills: Cerberus Fleet (Fleet Commander)")
    ).toBeTruthy();
    expect(screen.getByText("Heavy Missile Specialization")).toBeTruthy();
    expect(screen.getByText("2")).toBeTruthy();
    expect(screen.getByText("4")).toBeTruthy();

    // Skill level indicator icons rendered
    const indicator = screen.getByTestId("skill-level-indicator");
    expect(indicator).toBeTruthy();
    const icons = indicator.querySelectorAll("i");
    expect(icons).toHaveLength(5);
    expect(icons[0].className).toContain("text-success");
    expect(icons[1].className).toContain("text-success");
    expect(icons[2].className).toContain("text-danger");
    expect(icons[3].className).toContain("text-danger");
  });

  it("should display success alert when character has all required skills", async () => {
    // Test Data
    vi.mocked(ApiCalls.loadMissingSkills).mockResolvedValue({
      character_id: 99001,
      character_name: "Fleet Commander",
      doctrine_id: 1,
      doctrine_name: "Cerberus Fleet",
      missing_skills: [],
      clipboard_export: "",
    });

    // Test Action
    renderModal({
      characterId: 99001,
      doctrineId: 1,
      show: true,
      onHide: vi.fn(),
    });

    // Expected Result
    expect(
      await screen.findByText("Character has all required skills trained for this doctrine!")
    ).toBeTruthy();
  });

  it("should call onHide when close button is clicked", async () => {
    // Test Data
    const onHide = vi.fn();
    vi.mocked(ApiCalls.loadMissingSkills).mockResolvedValue({
      character_id: 99001,
      character_name: "Fleet Commander",
      doctrine_id: 1,
      doctrine_name: "Cerberus Fleet",
      missing_skills: [],
      clipboard_export: "",
    });

    // Test Action
    renderModal({
      characterId: 99001,
      doctrineId: 1,
      show: true,
      onHide,
    });

    await screen.findByText("Character has all required skills trained for this doctrine!");
    const closeBtns = screen.getAllByRole("button", { name: "Close" });
    fireEvent.click(closeBtns[0]);

    // Expected Result
    expect(onHide).toHaveBeenCalled();
  });
});
