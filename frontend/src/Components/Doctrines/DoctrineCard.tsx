// React
import React from "react";

// Third Party
import { AlertTriangle, CheckCircle2, Info, ShieldAlert } from "lucide-react";
import { Badge, Button, Card } from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA Memberaudit Doctrine Checker
import type { DoctrineItem } from "@/Components/Doctrines/types";

export interface DoctrineCardProps {
  doctrine: DoctrineItem;
  onViewSkills: (doctrineId: number) => void;
  onViewMissingSkills: (doctrineId: number) => void;
}

export const DoctrineCard: React.FC<DoctrineCardProps> = ({
  doctrine,
  onViewSkills,
  onViewMissingSkills,
}) => {
  const { t } = useTranslation();
  const hasMissing = doctrine.skills && doctrine.skills.length > 0;

  return (
    <Card
      className={`h-100 shadow-sm aa-panel border-0 ${hasMissing
        ? "border-start border-danger border-4"
        : "border-start border-success border-4"
        }`}
    >
      <Card.Body className="d-flex flex-column justify-content-between">
        <div>
          <div className="d-flex align-items-start justify-content-between gap-2 mb-2">
            <h6 className="mb-0 fw-bold">{doctrine.name}</h6>
            {hasMissing ? (
              <Badge bg="danger" className="d-flex align-items-center gap-1">
                <AlertTriangle size={12} />
                <span>
                  {doctrine.skills.length} {t("Missing")}
                </span>
              </Badge>
            ) : (
              <Badge bg="success" className="d-flex align-items-center gap-1">
                <CheckCircle2 size={12} />
                <span>{t("Ready")}</span>
              </Badge>
            )}
          </div>
        </div>

        <div className="d-flex align-items-center justify-content-end gap-2 mt-3 pt-2 border-top border-secondary-subtle">
          {doctrine.id ? (
            <Button
              variant="outline-secondary"
              size="sm"
              className="d-flex align-items-center gap-1 aa-btn aa-btn-secondary"
              onClick={() => onViewSkills(doctrine.id!)}
              title={t("View Required Skills")}
            >
              <Info size={14} />
              <span>{t("Skills")}</span>
            </Button>
          ) : null}

          {hasMissing && doctrine.id ? (
            <Button
              variant="outline-danger"
              size="sm"
              className="d-flex align-items-center gap-1 aa-btn aa-btn-danger"
              onClick={() => onViewMissingSkills(doctrine.id!)}
            >
              <ShieldAlert size={14} />
              <span>{t("Missing Skills")}</span>
            </Button>
          ) : null}
        </div>
      </Card.Body>
    </Card>
  );
};

export default DoctrineCard;
