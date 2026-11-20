// React
import React, { useMemo, useState } from "react";

// Third Party
import { useQuery } from "@tanstack/react-query";
import { BaseModal, BaseTable } from "aa-geuthur-react";
import type { BaseColumnDef } from "aa-geuthur-react";
import { Check, Clipboard, Copy, X } from "lucide-react";
import { Badge, Button } from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA Memberaudit Doctrine Checker
import { loadMissingSkills } from "@/Api/ApiCalls";
import { queryKeys } from "@/Api/query";
import { SkillLevelIndicator } from "@/Components/Badges/SkillLevelIndicator";

interface MissingSkillsModalProps {
  characterId: number | null;
  doctrineId: number | null;
  show: boolean;
  onHide: () => void;
}

interface MissingSkillRow {
  name: string;
  trained_level: number;
  needed_level: number;
}

export const MissingSkillsModal: React.FC<MissingSkillsModalProps> = ({
  characterId,
  doctrineId,
  show,
  onHide,
}) => {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);

  const { data, isLoading, isError, error } = useQuery({
    queryKey:
      characterId && doctrineId
        ? queryKeys.MissingSkills(characterId, doctrineId)
        : ["MissingSkills", 0, 0],
    queryFn: () => loadMissingSkills(characterId!, doctrineId!),
    enabled: Boolean(characterId && doctrineId && show),
  });

  const columns = useMemo<BaseColumnDef<MissingSkillRow>[]>(
    () => [
      {
        header: t("Skill"),
        accessorKey: "name",
        cell: ({ row }) => <span className="fw-semibold">{row.original.name}</span>,
      },
      {
        header: t("Current Level"),
        accessorKey: "trained_level",
        cell: ({ row }) => (
          <div className="text-center">
            <Badge bg="secondary">{row.original.trained_level}</Badge>
          </div>
        ),
      },
      {
        header: t("Required Level"),
        accessorKey: "needed_level",
        cell: ({ row }) => (
          <div className="text-center">
            <Badge bg="danger">{row.original.needed_level}</Badge>
          </div>
        ),
      },
      {
        header: t("Levels"),
        id: "levels",
        cell: ({ row }) => (
          <div className="text-center">
            <SkillLevelIndicator
              trainedLevel={row.original.trained_level}
              neededLevel={row.original.needed_level}
            />
          </div>
        ),
      },
    ],
    [t]
  );

  const handleCopyClipboard = async () => {
    if (!data?.clipboard_export) return;
    try {
      await navigator.clipboard.writeText(data.clipboard_export);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch (err) {
      console.error("Failed to copy skills to clipboard:", err);
    }
  };

  const modalFooter = (
    <div className="d-flex justify-content-end gap-2 w-100">
      {data && data.missing_skills.length > 0 && (
        <Button
          variant={copied ? "success" : "primary"}
          onClick={handleCopyClipboard}
          className="d-flex align-items-center gap-2"
        >
          {copied ? <Check size={16} /> : <Copy size={16} />}
          {copied ? t("Copied to Clipboard!") : t("Copy Skill Plan")}
        </Button>
      )}
      <Button variant="secondary" onClick={onHide} className="d-flex align-items-center gap-1">
        <X size={16} />
        {t("Close")}
      </Button>
    </div>
  );

  return (
    <BaseModal
      show={show}
      onHide={onHide}
      size="lg"
      title={
        <div className="d-flex align-items-center gap-2">
          <Clipboard size={20} />
          <span>
            {data
              ? `${t("Missing Skills")}: ${data.doctrine_name} (${data.character_name})`
              : t("Missing Skills")}
          </span>
        </div>
      }
      footer={modalFooter}
    >
      {isLoading && (
        <div className="d-flex justify-content-center align-items-center py-5 gap-2">
          <span className="spinner-border spinner-border-sm" role="status" />
          <span>{t("Loading missing skills...")}</span>
        </div>
      )}

      {isError && (
        <div className="alert alert-danger" role="alert">
          {error instanceof Error ? error.message : t("Failed to load missing skills.")}
        </div>
      )}

      {data && (
        <>
          {data.missing_skills.length === 0 ? (
            <div className="alert alert-success d-flex align-items-center gap-2 mb-0">
              <Check size={20} />
              <span>{t("Character has all required skills trained for this doctrine!")}</span>
            </div>
          ) : (
            <BaseTable
              columns={columns}
              data={data.missing_skills}
              pageSizeOptions={[10, 25, 50]}
              initialState={{
                pagination: { pageSize: 10 },
              }}
              striped
              hover
            />
          )}
        </>
      )}
    </BaseModal>
  );
};

export default MissingSkillsModal;
