// React
import React from "react";

// Third Party
import { PlusCircle } from "lucide-react";
import { Button } from "react-bootstrap";
import { useTranslation } from "react-i18next";

export interface ManageHeaderProps {
  onAddDoctrine: () => void;
}

export const ManageHeader: React.FC<ManageHeaderProps> = ({ onAddDoctrine }) => {
  const { t } = useTranslation();

  return (
    <div className="d-flex align-items-center justify-content-between flex-wrap gap-3 mt-3 mb-4">
      <div>
        <h4 className="mb-0 fw-bold">{t("Manage Doctrines")}</h4>
        <span className="text-muted small">
          {t("Configure doctrines, skill plans and audit settings")}
        </span>
      </div>

      <Button
        variant="primary"
        className="aa-btn aa-btn-primary d-flex align-items-center gap-2"
        onClick={onAddDoctrine}
      >
        <PlusCircle size={16} />
        <span>{t("Add Doctrine")}</span>
      </Button>
    </div>
  );
};

export default ManageHeader;
