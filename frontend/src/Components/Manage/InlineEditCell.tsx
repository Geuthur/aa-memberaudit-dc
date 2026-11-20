// React
import React, { useState } from "react";

// Third Party
import { Check, Pencil, X } from "lucide-react";
import { Button, Form, InputGroup } from "react-bootstrap";
import { useTranslation } from "react-i18next";

export interface InlineEditCellProps {
  value: string;
  label: string;
  type?: "text" | "number";
  disabled?: boolean;
  onSave: (value: string) => void;
  children?: React.ReactNode;
}

/**
 * Show a value and edit it in place: click the value, change it,
 * save with Enter or the check button, cancel with Escape.
 */
export const InlineEditCell: React.FC<InlineEditCellProps> = ({
  value,
  label,
  type = "text",
  disabled = false,
  onSave,
  children,
}) => {
  const { t } = useTranslation();
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState(value);

  const startEdit = () => {
    setDraft(value);
    setIsEditing(true);
  };

  const save = () => {
    setIsEditing(false);
    if (draft !== value) {
      onSave(draft);
    }
  };

  if (!isEditing) {
    return (
      <Button
        variant="link"
        className="p-0 text-reset text-decoration-none d-inline-flex align-items-center gap-2"
        aria-label={t("Edit {{label}}", { label })}
        title={t("Edit {{label}}", { label })}
        disabled={disabled}
        onClick={startEdit}
      >
        {children ?? <span>{value}</span>}
        <Pencil size={12} className="text-muted" />
      </Button>
    );
  }

  return (
    <InputGroup size="sm" className="flex-nowrap">
      <Form.Control
        autoFocus
        type={type}
        aria-label={label}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") save();
          if (e.key === "Escape") setIsEditing(false);
        }}
      />
      <Button variant="success" aria-label={t("Save")} onClick={save}>
        <Check size={14} />
      </Button>
      <Button
        variant="secondary"
        aria-label={t("Cancel")}
        onClick={() => setIsEditing(false)}
      >
        <X size={14} />
      </Button>
    </InputGroup>
  );
};

export default InlineEditCell;
