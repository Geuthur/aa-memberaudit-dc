// React
import React from "react";

// Third Party
import { User } from "lucide-react";
import { Button, Card } from "react-bootstrap";

// AA Memberaudit Doctrine Checker
import type { CharacterDoctrines } from "@/Api/schema";

export interface CharacterSelectorProps {
  characters: CharacterDoctrines[];
  selectedCharId: number;
  onSelectCharacter: (charId: number) => void;
}

export const CharacterSelector: React.FC<CharacterSelectorProps> = ({
  characters,
  selectedCharId,
  onSelectCharacter,
}) => {
  if (characters.length <= 1) return null;

  return (
    <Card className="mb-4 aa-panel shadow-sm">
      <Card.Body className="p-2 d-flex flex-wrap gap-2">
        {characters.map((cd) => {
          const isActive = selectedCharId === cd.character.character_id;
          return (
            <Button
              key={cd.character.character_id}
              variant={isActive ? "primary" : "secondary"}
              className={`aa-btn ${
                isActive ? "aa-btn-primary" : "aa-btn-secondary"
              }`}
              onClick={() => onSelectCharacter(cd.character.character_id)}
            >
              <User size={16} />
              <span>{cd.character.character_name}</span>
            </Button>
          );
        })}
      </Card.Body>
    </Card>
  );
};

export default CharacterSelector;
