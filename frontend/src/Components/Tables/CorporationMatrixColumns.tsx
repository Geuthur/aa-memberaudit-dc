// Third Party
import type { BaseColumnDef } from "aa-geuthur-react";
import type { TFunction } from "i18next";
import { AlertTriangle, BookOpen, CheckCircle2 } from "lucide-react";
import { Badge } from "react-bootstrap";

// AA Memberaudit Doctrine Checker
import type { ActiveDoctrineOverview } from "@/Api/schema";
import type { DoctrineStatus, MemberDoctrineRow } from "@/Components/Corporation/types";

export const getCorporationMatrixColumns = (
  t: TFunction,
  activeDoctrines: ActiveDoctrineOverview[],
  onOpenSkills: (doctrineId: number, characterId?: number) => void,
  onOpenMissingSkills: (charId: number, doctrineId: number) => void
): BaseColumnDef<MemberDoctrineRow>[] => {
  const cols: BaseColumnDef<MemberDoctrineRow>[] = [
    {
      header: () => <span style={{ whiteSpace: "nowrap" }}>{t("Member")}</span>,
      accessorFn: (row) => row.character.character_name,
      id: "member",
      cell: ({ row }) => {
        const member = row.original;
        return (
          <div
            className="d-flex align-items-center gap-2"
            style={{ minWidth: "160px", whiteSpace: "nowrap" }}
          >
            <img
              src={`https://images.evetech.net/characters/${member.character.character_id}/portrait?size=32`}
              alt={member.character.character_name}
              className="rounded-circle flex-shrink-0"
              width={28}
              height={28}
            />
            <div className="text-truncate">
              <div className="fw-semibold text-truncate">
                {member.character.character_name}
              </div>
              {member.alts && member.alts.length > 0 && (
                <div className="text-muted small" style={{ fontSize: "0.75rem" }}>
                  +{member.alts.length} {t("alts")}
                </div>
              )}
            </div>
          </div>
        );
      },
    },
  ];

  activeDoctrines.forEach((d) => {
    cols.push({
      id: `doctrine_${d.id || d.name}`,
      header: () => (
        <div
          role="button"
          style={{ cursor: "pointer", whiteSpace: "nowrap" }}
          onClick={() => d.id && onOpenSkills(d.id)}
          className="d-inline-flex align-items-center gap-1 justify-content-center w-100"
          title={d.category}
        >
          <span>{d.name}</span>
          <BookOpen size={11} className="text-muted" />
        </div>
      ),
      cell: ({ row }) => {
        const member = row.original;
        if (!member.isAudited) {
          return (
            <div className="text-center">
              <span
                className="spinner-border spinner-border-sm text-secondary opacity-50"
                style={{ width: "12px", height: "12px" }}
                title={t("Auditing...")}
              />
            </div>
          );
        }

        const doc = member.doctrines?.[d.name] as DoctrineStatus | undefined;
        if (!doc) {
          return <div className="text-center text-muted">-</div>;
        }
        const hasMissing = doc.skills && doc.skills.length > 0;
        return (
          <div className="text-center">
            {hasMissing ? (
              <Badge
                bg="danger"
                className="d-inline-flex align-items-center gap-1"
                role="button"
                style={{ cursor: "pointer" }}
                onClick={() =>
                  (doc.id || d.id) &&
                  onOpenMissingSkills(
                    member.character.character_id,
                    doc.id || d.id!
                  )
                }
                title={`${doc.skills.length} ${t("missing skills")} - ${t(
                  "Click to view"
                )}`}
              >
                <AlertTriangle size={12} />
                <span>{t("Not Ready")}</span>
              </Badge>
            ) : (
              <Badge
                bg="success"
                className="d-inline-flex align-items-center gap-1"
                role="button"
                style={{ cursor: "pointer" }}
                onClick={() =>
                  (doc.id || d.id) && onOpenSkills(doc.id || d.id!, member.character.character_id)
                }
                title={t("Doctrine Ready")}
              >
                <CheckCircle2 size={12} />
                <span>{t("Ready")}</span>
              </Badge>
            )}
          </div>
        );
      },
    });
  });

  return cols;
};
