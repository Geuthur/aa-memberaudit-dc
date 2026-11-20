// React
import React from "react";

// Third Party
import { BookOpen, Building2, LayoutGrid, List, Users } from "lucide-react";
import { Button, ButtonGroup, Card, ProgressBar } from "react-bootstrap";
import { useTranslation } from "react-i18next";

export interface CorporationHeaderProps {
  corpId: number;
  corpName: string;
  auditedCount: number;
  totalMembersCount: number;
  activeDoctrinesCount: number;
  isAuditing: boolean;
  auditProgressPercent: number;
  viewMode: "badges" | "matrix";
  onViewModeChange: (mode: "badges" | "matrix") => void;
}

export const CorporationHeader: React.FC<CorporationHeaderProps> = ({
  corpId,
  corpName,
  auditedCount,
  totalMembersCount,
  activeDoctrinesCount,
  isAuditing,
  auditProgressPercent,
  viewMode,
  onViewModeChange,
}) => {
  const { t } = useTranslation();

  return (
    <Card className="mb-4 aa-panel shadow-sm">
      <Card.Body className="d-flex align-items-center justify-content-between flex-wrap gap-3">
        <div className="d-flex align-items-center gap-3">
          {corpId > 0 && (
            <img
              src={`https://images.evetech.net/corporations/${corpId}/logo?size=64`}
              alt="Corporation Logo"
              className="rounded border"
              width={56}
              height={56}
            />
          )}
          <div>
            <h4 className="mb-0 fw-bold d-flex align-items-center gap-2">
              <Building2 size={22} className="text-primary" />
              {corpName}
            </h4>
            <div className="text-muted small d-flex align-items-center gap-3 mt-1 flex-wrap">
              <span className="d-flex align-items-center gap-1">
                <Users size={14} />
                {auditedCount} / {totalMembersCount} {t("Members audited")}
                {isAuditing && (
                  <span
                    className="spinner-border spinner-border-sm text-primary ms-1"
                    style={{ width: "12px", height: "12px" }}
                  />
                )}
              </span>
              <span className="d-flex align-items-center gap-1">
                <BookOpen size={14} />
                {activeDoctrinesCount} {t("Active doctrines")}
              </span>
            </div>
          </div>
        </div>

        {/* View mode toggle */}
        <div className="d-flex align-items-center gap-2">
          <ButtonGroup size="sm">
            <Button
              variant={viewMode === "badges" ? "primary" : "secondary"}
              className={`aa-btn aa-btn-sm ${
                viewMode === "badges" ? "aa-btn-primary" : "aa-btn-secondary"
              }`}
              onClick={() => onViewModeChange("badges")}
              title={t("Badges View")}
            >
              <List size={16} />
              <span className="d-none d-sm-inline">{t("Badges")}</span>
            </Button>
            <Button
              variant={viewMode === "matrix" ? "primary" : "secondary"}
              className={`aa-btn aa-btn-sm ${
                viewMode === "matrix" ? "aa-btn-primary" : "aa-btn-secondary"
              }`}
              onClick={() => onViewModeChange("matrix")}
              title={t("Matrix View")}
            >
              <LayoutGrid size={16} />
              <span className="d-none d-sm-inline">{t("Matrix")}</span>
            </Button>
          </ButtonGroup>
        </div>
      </Card.Body>

      {isAuditing && (
        <ProgressBar
          animated
          now={auditProgressPercent}
          variant="primary"
          style={{ height: "4px" }}
          className="rounded-0"
        />
      )}
    </Card>
  );
};

export default CorporationHeader;
