// React
import React from "react";

// Third Party
import { Building2, User } from "lucide-react";
import { Badge, Button, Card } from "react-bootstrap";
import { useTranslation } from "react-i18next";

export interface OverviewNavProps {
  activeTab: "account" | "corporation";
  onTabChange: (tab: "account" | "corporation") => void;
  accountCount?: number;
  corpCount?: number;
  canViewCorp: boolean;
}

export const OverviewNav: React.FC<OverviewNavProps> = ({
  activeTab,
  onTabChange,
  accountCount,
  corpCount,
  canViewCorp,
}) => {
  const { t } = useTranslation();

  return (
    <Card className="mt-3 mb-4 aa-panel border-0 shadow-sm">
      <Card.Body className="p-2 d-flex flex-wrap gap-2">
        <Button
          variant={activeTab === "account" ? "primary" : "secondary"}
          className={`aa-btn ${
            activeTab === "account" ? "aa-btn-primary" : "aa-btn-secondary"
          }`}
          onClick={() => onTabChange("account")}
        >
          <User size={16} />
          <span>{t("Account Overview")}</span>
          {typeof accountCount === "number" && (
            <Badge bg="secondary" pill>
              {accountCount}
            </Badge>
          )}
        </Button>

        {canViewCorp && (
          <Button
            variant={activeTab === "corporation" ? "primary" : "secondary"}
            className={`aa-btn ${
              activeTab === "corporation" ? "aa-btn-primary" : "aa-btn-secondary"
            }`}
            onClick={() => onTabChange("corporation")}
          >
            <Building2 size={16} />
            <span>{t("Corporation Overview")}</span>
            {typeof corpCount === "number" && (
              <Badge bg="secondary" pill>
                {corpCount}
              </Badge>
            )}
          </Button>
        )}
      </Card.Body>
    </Card>
  );
};

export default OverviewNav;
