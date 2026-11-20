// React
import React from "react";

// Third Party
import { Card } from "react-bootstrap";

// AA Memberaudit Doctrine Checker
import type { CharacterSchema } from "@/Api/schema";

export interface CharacterBannerProps {
  character: CharacterSchema;
}

export const CharacterBanner: React.FC<CharacterBannerProps> = ({ character }) => {
  return (
    <Card className="mb-4 aa-panel shadow-sm">
      <Card.Body className="d-flex align-items-center justify-content-between flex-wrap gap-3">
        <div className="d-flex align-items-center gap-3">
          <img
            src={`https://images.evetech.net/characters/${character.character_id}/portrait?size=64`}
            alt={character.character_name}
            className="rounded-circle border border-2 border-primary"
            width={56}
            height={56}
          />
          <div>
            <h4 className="mb-0 fw-bold">{character.character_name}</h4>
            <span className="text-muted small">
              {character.corporation_name}
              {character.alliance_name ? ` • ${character.alliance_name}` : ""}
            </span>
          </div>
        </div>
      </Card.Body>
    </Card>
  );
};

export default CharacterBanner;
