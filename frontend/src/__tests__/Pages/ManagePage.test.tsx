// React
import { MemoryRouter } from "react-router-dom";

// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA Memberaudit Doctrine Checker
import * as manageCalls from "@/Api/calls/manage";
import ManagePage from "@/Pages/ManagePage";

vi.mock("@/Api/calls/manage", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/Api/calls/manage")>()),
  loadManageDoctrines: vi.fn(),
  deleteSkillList: vi.fn(),
  updateSkillList: vi.fn(),
}));

// A stable `t` like the one of i18next: a new one per render rebuilds the columns
const t = (key: string) => key;
vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t }),
  withTranslation: () => (Component: unknown) => Component,
}));

const renderPage = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/madc/manage/"]}>
        <ManagePage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe("ManagePage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render manage doctrines table and add button", async () => {
    // Test Data
    vi.mocked(manageCalls.loadManageDoctrines).mockResolvedValue([
      {
        id: 1,
        name: "Cerberus Fleet",
        category: "Cruiser",
        ordering: 1,
        active: true,
        skill_count: 5,
      },
    ]);

    // Test Action
    renderPage();

    // Expected Result
    expect(await screen.findByText("Cerberus Fleet")).toBeTruthy();
    expect(screen.getByText("Cruiser")).toBeTruthy();
    expect(screen.getByText("Add Doctrine")).toBeTruthy();
    expect(screen.getByText("5 skills")).toBeTruthy();
  });

  it("should render the row actions as icon buttons in a button group", async () => {
    // Test Data
    vi.mocked(manageCalls.loadManageDoctrines).mockResolvedValue([
      {
        id: 1,
        name: "Cerberus Fleet",
        category: "Cruiser",
        ordering: 1,
        active: true,
        skill_count: 5,
      },
    ]);

    // Test Action
    renderPage();

    // Expected Result
    await screen.findByText("Cerberus Fleet");
    const view = screen.getByLabelText("View Skills");
    const edit = screen.getByLabelText("Edit Doctrine");
    const remove = screen.getByLabelText("Delete Doctrine");
    expect(view.parentElement?.classList.contains("btn-group-sm")).toBe(true);
    expect(edit.parentElement).toBe(view.parentElement);
    expect(remove.parentElement).toBe(view.parentElement);
  });

  const skillList = {
    id: 1,
    name: "Cerberus Fleet",
    category: "Cruiser",
    ordering: 1,
    active: true,
    skill_count: 5,
  };

  it("should save an inline edited name with Enter", async () => {
    // Test Data
    vi.mocked(manageCalls.loadManageDoctrines).mockResolvedValue([skillList]);
    vi.mocked(manageCalls.updateSkillList).mockResolvedValue({
      ...skillList,
      name: "Cerberus Doctrine",
    });

    // Test Action
    renderPage();
    const nameButton = (await screen.findByText("Cerberus Fleet")).closest("button");
    fireEvent.click(nameButton!);
    const input = screen.getByLabelText("Doctrine Name");
    fireEvent.change(input, { target: { value: "Cerberus Doctrine" } });
    fireEvent.keyDown(input, { key: "Enter" });

    // Expected Result
    await waitFor(() =>
      expect(manageCalls.updateSkillList).toHaveBeenCalledWith(1, {
        name: "Cerberus Doctrine",
      })
    );
    expect(await screen.findByText("Cerberus Doctrine")).toBeTruthy();
  });

  it("should save an inline edited ordering as number", async () => {
    // Test Data
    vi.mocked(manageCalls.loadManageDoctrines).mockResolvedValue([skillList]);
    vi.mocked(manageCalls.updateSkillList).mockResolvedValue({ ...skillList, ordering: 7 });

    // Test Action
    renderPage();
    await screen.findByText("Cerberus Fleet");
    fireEvent.click(screen.getByText("1").closest("button")!);
    const input = screen.getByLabelText("Order Weight");
    fireEvent.change(input, { target: { value: "7" } });
    fireEvent.click(screen.getByLabelText("Save"));

    // Expected Result
    await waitFor(() =>
      expect(manageCalls.updateSkillList).toHaveBeenCalledWith(1, { ordering: 7 })
    );
  });

  it("should not save when the inline edit is cancelled with Escape", async () => {
    // Test Data
    vi.mocked(manageCalls.loadManageDoctrines).mockResolvedValue([skillList]);

    // Test Action
    renderPage();
    fireEvent.click((await screen.findByText("Cruiser")).closest("button")!);
    const input = screen.getByLabelText("Category");
    fireEvent.change(input, { target: { value: "Battleship" } });
    fireEvent.keyDown(input, { key: "Escape" });

    // Expected Result
    expect(manageCalls.updateSkillList).not.toHaveBeenCalled();
    expect(screen.getByText("Cruiser")).toBeTruthy();
  });

  it("should toggle the active flag", async () => {
    // Test Data
    vi.mocked(manageCalls.loadManageDoctrines).mockResolvedValue([skillList]);
    vi.mocked(manageCalls.updateSkillList).mockResolvedValue({ ...skillList, active: false });

    // Test Action
    renderPage();
    await screen.findByText("Cerberus Fleet");
    fireEvent.click(screen.getByLabelText("Deactivate"));

    // Expected Result
    await waitFor(() =>
      expect(manageCalls.updateSkillList).toHaveBeenCalledWith(1, { active: false })
    );
    expect(await screen.findByText("Inactive")).toBeTruthy();
  });

  it("should show the API error when an update fails", async () => {
    // Test Data
    vi.mocked(manageCalls.loadManageDoctrines).mockResolvedValue([skillList]);
    vi.mocked(manageCalls.updateSkillList).mockRejectedValue(
      new Error("Skill list with this name already exists")
    );

    // Test Action
    renderPage();
    await screen.findByText("Cerberus Fleet");
    fireEvent.click(screen.getByLabelText("Deactivate"));

    // Expected Result
    expect(
      await screen.findByText("Skill list with this name already exists")
    ).toBeTruthy();
  });

  it("should keep the inline input and show the error when saving fails", async () => {
    // Test Data
    vi.mocked(manageCalls.loadManageDoctrines).mockResolvedValue([skillList]);
    vi.mocked(manageCalls.updateSkillList).mockRejectedValue(
      new Error("Skill list with this name already exists")
    );

    // Test Action
    renderPage();
    fireEvent.click((await screen.findByText("Cerberus Fleet")).closest("button")!);
    fireEvent.change(screen.getByLabelText("Doctrine Name"), {
      target: { value: "Taken Name" },
    });
    fireEvent.keyDown(screen.getByLabelText("Doctrine Name"), { key: "Enter" });

    // Expected Result
    expect(
      await screen.findByText("Skill list with this name already exists")
    ).toBeTruthy();
    const input = screen.getByLabelText("Doctrine Name") as HTMLInputElement;
    expect(input.value).toBe("Taken Name");
    await waitFor(() => expect(input.readOnly).toBe(false));
  });

  it("should send an empty text to remove the category inline", async () => {
    // Test Data
    vi.mocked(manageCalls.loadManageDoctrines).mockResolvedValue([skillList]);
    vi.mocked(manageCalls.updateSkillList).mockResolvedValue({
      ...skillList,
      category: null,
    });

    // Test Action
    renderPage();
    fireEvent.click((await screen.findByText("Cruiser")).closest("button")!);
    const input = screen.getByLabelText("Category");
    fireEvent.change(input, { target: { value: "" } });
    fireEvent.keyDown(input, { key: "Enter" });

    // Expected Result
    await waitFor(() =>
      expect(manageCalls.updateSkillList).toHaveBeenCalledWith(1, { category: "" })
    );
    expect(await screen.findByText("Uncategorized")).toBeTruthy();
  });

  it("should ignore an empty inline ordering", async () => {
    // Test Data
    vi.mocked(manageCalls.loadManageDoctrines).mockResolvedValue([skillList]);

    // Test Action
    renderPage();
    await screen.findByText("Cerberus Fleet");
    fireEvent.click(screen.getByText("1").closest("button")!);
    const input = screen.getByLabelText("Order Weight");
    fireEvent.change(input, { target: { value: "" } });
    fireEvent.keyDown(input, { key: "Enter" });

    // Expected Result
    expect(manageCalls.updateSkillList).not.toHaveBeenCalled();
  });
});
