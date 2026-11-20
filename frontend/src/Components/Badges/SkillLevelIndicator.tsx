// React
import React from "react";

export interface SkillLevelIndicatorProps {
  /** Character's currently trained skill level (0 - 5) */
  trainedLevel?: number;
  /** Skill level required by the doctrine (1 - 5) */
  neededLevel?: number;
  /** Required skill level when displaying doctrine info without a character context (1 - 5) */
  requiredLevel?: number;
  /** Style for missing levels: "danger" (red) or "white" */
  missingVariant?: "danger" | "white";
  /** Optional additional CSS class name */
  className?: string;
}

const ALL_LEVELS = [1, 2, 3, 4, 5];

/**
 * SkillLevelIndicator renders skill levels 1-5 with FontAwesome circle icons:
 * - Green (`text-success`): already learned level
 * - Red (`text-danger`) or White (`text-white`): missing level needed for requirement
 * - Dimmed White (`text-white opacity-25`): untargeted remaining levels
 */
export const SkillLevelIndicator: React.FC<SkillLevelIndicatorProps> = ({
  trainedLevel,
  neededLevel,
  requiredLevel,
  missingVariant = "danger",
  className = "",
}) => {
  const effectiveNeeded = neededLevel ?? requiredLevel ?? 0;
  const effectiveTrained = trainedLevel ?? 0;
  const hasCharacterContext = trainedLevel !== undefined;

  return (
    <div
      className={`d-inline-flex align-items-center gap-1 ${className}`}
      data-testid="skill-level-indicator"
    >
      {ALL_LEVELS.map((level) => {
        let colorClass: string;
        let statusText: string;

        if (hasCharacterContext) {
          if (level <= effectiveTrained) {
            colorClass = "text-success";
            statusText = "Learned";
          } else if (level <= effectiveNeeded) {
            colorClass = missingVariant === "white" ? "text-white" : "text-danger";
            statusText = "Missing";
          } else {
            colorClass = "text-white opacity-25";
            statusText = "Not required";
          }
        } else {
          // Doctrine info view (required level display)
          if (level <= effectiveNeeded) {
            colorClass = "text-white";
            statusText = "Required";
          } else {
            colorClass = "text-white opacity-25";
            statusText = "Not required";
          }
        }

        return (
          <i
            key={level}
            className={`fas fa-circle ${colorClass}`}
            title={`Level ${level} (${statusText})`}
            aria-label={`Level ${level} (${statusText})`}
            style={{
              fontSize: "0.7rem",
              filter: "drop-shadow(0 0 1px rgba(0, 0, 0, 0.5))",
            }}
          />
        );
      })}
    </div>
  );
};

export default SkillLevelIndicator;
