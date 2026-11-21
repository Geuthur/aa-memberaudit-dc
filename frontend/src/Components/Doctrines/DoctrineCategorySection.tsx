// React
import React from "react";

// Third Party
import { BookOpen } from "lucide-react";
import { Badge, Col, Row } from "react-bootstrap";

// AA Memberaudit Doctrine Checker
import { DoctrineCard } from "@/Components/Doctrines/DoctrineCard";
import type { DoctrineItem } from "@/Components/Doctrines/types";

export interface DoctrineCategorySectionProps {
  category: string;
  doctrines: DoctrineItem[];
  onViewSkills: (doctrineId: number) => void;
  onViewMissingSkills: (doctrineId: number) => void;
}

export const DoctrineCategorySection: React.FC<DoctrineCategorySectionProps> = ({
  category,
  doctrines,
  onViewSkills,
  onViewMissingSkills,
}) => {
  return (
    <div className="mb-4">
      <div className="d-flex align-items-center gap-2 mb-3">
        <BookOpen size={20} className="text-primary" />
        <h5 className="mb-0 fw-bold">{category}</h5>
        <Badge bg="secondary" pill>
          {doctrines.length}
        </Badge>
      </div>

      <Row xs={1} md={2} lg={3} className="g-3">
        {doctrines.map((doc) => (
          <Col key={doc.name}>
            <DoctrineCard
              doctrine={doc}
              onViewSkills={onViewSkills}
              onViewMissingSkills={onViewMissingSkills}
            />
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default DoctrineCategorySection;
