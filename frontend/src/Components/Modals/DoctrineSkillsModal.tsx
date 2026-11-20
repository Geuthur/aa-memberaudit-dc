// React
import React, { useMemo, useState } from "react";

// Third Party
import { useQuery } from "@tanstack/react-query";
import { BaseModal, BaseTable } from "aa-geuthur-react";
import type { BaseColumnDef } from "aa-geuthur-react";
import { BookOpen, Search, X } from "lucide-react";
import { Badge, Button, Form, InputGroup } from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA Memberaudit Doctrine Checker
import { loadDoctrineSkills } from "@/Api/ApiCalls";
import { queryKeys } from "@/Api/query";
import { SkillLevelIndicator } from "@/Components/Badges/SkillLevelIndicator";

export interface DoctrineSkillsModalProps {
  doctrineId: number | null;
  characterId?: number | null;
  show: boolean;
  onHide: () => void;
}

interface DoctrineSkillRow {
  skillName: string;
  level: number;
  trainedLevel?: number;
}

export const DoctrineSkillsModal: React.FC<DoctrineSkillsModalProps> = ({
  doctrineId,
  characterId,
  show,
  onHide,
}) => {
  const { t } = useTranslation();
  const [search, setSearch] = useState("");

  const { data, isLoading, isError, error } = useQuery({
    queryKey: doctrineId
      ? queryKeys.DoctrineSkills(doctrineId, characterId)
      : ["DoctrineSkills", 0, 0],
    queryFn: () => loadDoctrineSkills(doctrineId!, characterId),
    enabled: Boolean(doctrineId && show),
  });

  const skillsData = useMemo<DoctrineSkillRow[]>(() => {
    if (!data?.skills) return [];
    return Object.entries(data.skills).map(([skillName, level]) => ({
      skillName,
      level: Number(level),
      trainedLevel: data.character_skills
        ? data.character_skills[skillName] ?? 0
        : undefined,
    }));
  }, [data]);

  const filteredSkillsData = useMemo(() => {
    if (!search.trim()) return skillsData;
    const lower = search.toLowerCase();
    return skillsData.filter((row) => row.skillName.toLowerCase().includes(lower));
  }, [skillsData, search]);

  const columns = useMemo<BaseColumnDef<DoctrineSkillRow>[]>(
    () => [
      {
        header: t("Skill Name"),
        accessorKey: "skillName",
        cell: ({ row }) => <span className="fw-semibold">{row.original.skillName}</span>,
      },
      {
        header: t("Required Level"),
        accessorKey: "level",
        cell: ({ row }) => (
          <div className="text-center">
            <Badge bg="primary">{row.original.level}</Badge>
          </div>
        ),
      },
      {
        header: t("Levels"),
        id: "levels",
        enableSorting: false,
        cell: ({ row }) => (
          <div className="text-center">
            <SkillLevelIndicator
              trainedLevel={row.original.trainedLevel}
              neededLevel={row.original.level}
              requiredLevel={row.original.level}
              missingVariant="white"
            />
          </div>
        ),
      },
    ],
    [t]
  );

  const handleClose = () => {
    setSearch("");
    onHide();
  };

  const modalFooter = (
    <div className="d-flex justify-content-end gap-2 w-100">
      <Button variant="secondary" onClick={handleClose} className="d-flex align-items-center gap-1">
        <X size={16} />
        {t("Close")}
      </Button>
    </div>
  );

  return (
    <BaseModal
      show={show}
      onHide={handleClose}
      size="lg"
      title={
        <div className="d-flex align-items-center gap-2">
          <BookOpen size={20} />
          <span>{data ? `${t("Required Skills")}: ${data.name}` : t("Required Skills")}</span>
        </div>
      }
      footer={modalFooter}
    >
      {isLoading && (
        <div className="d-flex justify-content-center align-items-center py-5 gap-2">
          <span className="spinner-border spinner-border-sm" role="status" />
          <span>{t("Loading skills...")}</span>
        </div>
      )}

      {isError && (
        <div className="alert alert-danger" role="alert">
          {error instanceof Error ? error.message : t("Failed to load doctrine skills.")}
        </div>
      )}

      {data && (
        <>
          <div className="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3 px-1">
            <div className="d-flex align-items-center gap-3 text-muted small">
              <span>
                {t("Category")}: <Badge bg="info">{data.category || t("Uncategorized")}</Badge>
              </span>
              <span>
                {t("Total Skills")}: <Badge bg="secondary">{skillsData.length}</Badge>
              </span>
            </div>

            {skillsData.length > 5 && (
              <div style={{ maxWidth: "250px", width: "100%" }}>
                <InputGroup size="sm">
                  <InputGroup.Text className="bg-transparent border-secondary text-muted">
                    <Search size={14} />
                  </InputGroup.Text>
                  <Form.Control
                    type="text"
                    placeholder={t("Filter skills...")}
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="border-secondary"
                  />
                  {search && (
                    <Button
                      variant="outline-secondary"
                      size="sm"
                      onClick={() => setSearch("")}
                    >
                      <X size={14} />
                    </Button>
                  )}
                </InputGroup>
              </div>
            )}
          </div>

          {skillsData.length === 0 ? (
            <div className="alert alert-info">
              {t("No required skills defined for this doctrine.")}
            </div>
          ) : (
            <BaseTable
              columns={columns}
              data={filteredSkillsData}
              pageSizeOptions={[10, 25, 50]}
              initialState={{
                pagination: { pageSize: 10 },
              }}
              emptyText={t("No matching skills found.")}
              striped
              hover
            />
          )}
        </>
      )}
    </BaseModal>
  );
};

export default DoctrineSkillsModal;
