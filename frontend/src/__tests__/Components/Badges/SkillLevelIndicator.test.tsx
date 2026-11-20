// Third Party
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

// AA Memberaudit Doctrine Checker
import { SkillLevelIndicator } from "@/Components/Badges/SkillLevelIndicator";

describe("SkillLevelIndicator", () => {
  it("should render 5 circles with green for learned and red for missing when character context is provided", () => {
    // Test Data: character has trained level 2, doctrine requires level 4
    render(<SkillLevelIndicator trainedLevel={2} neededLevel={4} />);

    // Test Action
    const indicator = screen.getByTestId("skill-level-indicator");
    const icons = indicator.querySelectorAll("i");

    // Expected Result: 5 circles rendered
    expect(icons).toHaveLength(5);

    // Levels 1 and 2: Learned (text-success)
    expect(icons[0].className).toContain("text-success");
    expect(icons[0].className).toContain("fas fa-circle");
    expect(icons[1].className).toContain("text-success");

    // Levels 3 and 4: Missing (text-danger)
    expect(icons[2].className).toContain("text-danger");
    expect(icons[3].className).toContain("text-danger");

    // Level 5: Untargeted info (text-white)
    expect(icons[4].className).toContain("text-white");
  });

  it("should render all circles as green when skill is fully trained to requirement", () => {
    // Test Data: character has trained level 5, needed level 5
    render(<SkillLevelIndicator trainedLevel={5} neededLevel={5} />);

    // Test Action
    const indicator = screen.getByTestId("skill-level-indicator");
    const icons = indicator.querySelectorAll("i");

    // Expected Result
    expect(icons).toHaveLength(5);
    icons.forEach((icon) => {
      expect(icon.className).toContain("text-success");
    });
  });

  it("should render all needed circles as red when character has trained level 0", () => {
    // Test Data: untrained skill, doctrine requires level 3
    render(<SkillLevelIndicator trainedLevel={0} neededLevel={3} />);

    // Test Action
    const indicator = screen.getByTestId("skill-level-indicator");
    const icons = indicator.querySelectorAll("i");

    // Expected Result: levels 1-3 missing, 4-5 info
    expect(icons[0].className).toContain("text-danger");
    expect(icons[1].className).toContain("text-danger");
    expect(icons[2].className).toContain("text-danger");
    expect(icons[3].className).toContain("text-white");
    expect(icons[4].className).toContain("text-white");
  });

  it("should render white info circles for doctrine requirement view without character context", () => {
    // Test Data: doctrine requirement level 3
    render(<SkillLevelIndicator requiredLevel={3} />);

    // Test Action
    const indicator = screen.getByTestId("skill-level-indicator");
    const icons = indicator.querySelectorAll("i");

    // Expected Result: levels 1-3 required info (text-white)
    expect(icons).toHaveLength(5);
    expect(icons[0].className).toContain("text-white");
    expect(icons[1].className).toContain("text-white");
    expect(icons[2].className).toContain("text-white");
    expect(icons[3].className).toContain("opacity-25");
    expect(icons[4].className).toContain("opacity-25");
  });

  it("should render green for trained levels and white for missing levels when missingVariant is white", () => {
    // Test Data: character trained level 2, required level 4, missingVariant="white"
    render(
      <SkillLevelIndicator
        trainedLevel={2}
        neededLevel={4}
        missingVariant="white"
      />
    );

    // Test Action
    const indicator = screen.getByTestId("skill-level-indicator");
    const icons = indicator.querySelectorAll("i");

    // Expected Result: levels 1-2 green (text-success), 3-4 white (text-white), 5 opacity-25
    expect(icons).toHaveLength(5);
    expect(icons[0].className).toContain("text-success");
    expect(icons[1].className).toContain("text-success");
    expect(icons[2].className).toContain("text-white");
    expect(icons[3].className).toContain("text-white");
    expect(icons[4].className).toContain("opacity-25");
  });
});
