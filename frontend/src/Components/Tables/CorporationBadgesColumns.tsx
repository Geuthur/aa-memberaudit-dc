// Third Party
import type { BaseColumnDef } from "aa-geuthur-react";
import type { TFunction } from "i18next";
import { AlertTriangle, CheckCircle2 } from "lucide-react";
import { Badge, ProgressBar } from "react-bootstrap";

// AA Memberaudit Doctrine Checker
import type { ActiveDoctrineOverview } from "@/Api/schema";
import type { DoctrineStatus, MemberDoctrineRow } from "@/Components/Corporation/types";

export const getCorporationBadgesColumns = (
  t: TFunction,
  activeDoctrines: ActiveDoctrineOverview[],
  onOpenSkills: (doctrineId: number, characterId?: number) => void,
  onOpenMissingSkills: (charId: number, doctrineId: number) => void
): BaseColumnDef<MemberDoctrineRow>[] => [
  {
    header: t("Member"),
    accessorFn: (row) => row.character.character_name,
    id: "member",
    cell: ({ row }) => {
      const member = row.original;
      return (
        <div className="d-flex align-items-center gap-2">
          <img
            src={`https://images.evetech.net/characters/${member.character.character_id}/portrait?size=32`}
            alt={member.character.character_name}
            className="rounded-circle"
            width={32}
            height={32}
          />
          <div>
            <div className="fw-semibold">{member.character.character_name}</div>
            {member.alts && member.alts.length > 0 && (
              <div
                className="text-muted small"
                style={{ fontSize: "0.75rem" }}
                title={member.alts.map((a) => a.character_name).join(", ")}
              >
                +{member.alts.length} {t("alts")}
              </div>
            )}
          </div>
        </div>
      );
    },
  },
  {
    header: t("Readiness"),
    id: "readiness",
    accessorFn: (member) => {
      if (!member.isAudited) return -1;
      const memberDocs = activeDoctrines
        .map((d) => member.doctrines?.[d.name] as DoctrineStatus | undefined)
        .filter(Boolean);
      const readyCount = memberDocs.filter((d) => !d?.skills || d.skills.length === 0).length;
      const totalCount = memberDocs.length;
      return totalCount > 0 ? readyCount / totalCount : 0;
    },
    cell: ({ row }) => {
      const member = row.original;
      if (!member.isAudited) {
        return (
          <div className="d-flex flex-column align-items-center gap-1">
            <Badge
              bg="secondary"
              className="d-inline-flex align-items-center gap-1 opacity-75"
            >
              <span
                className="spinner-border spinner-border-sm"
                style={{ width: "10px", height: "10px" }}
              />
              <span>{t("Auditing...")}</span>
            </Badge>
            <ProgressBar
              animated
              now={100}
              variant="secondary"
              style={{ width: "90px", height: "6px" }}
            />
          </div>
        );
      }

      const memberDoctrines = activeDoctrines
        .map((d) => member.doctrines?.[d.name] as DoctrineStatus | undefined)
        .filter(Boolean);
      const readyCount = memberDoctrines.filter((d) => !d?.skills || d.skills.length === 0).length;
      const totalCount = memberDoctrines.length;
      const percent = totalCount > 0 ? Math.round((readyCount / totalCount) * 100) : 0;

      return (
        <div className="d-flex flex-column align-items-center gap-1">
          <Badge
            bg={
              readyCount === totalCount && totalCount > 0
                ? "success"
                : readyCount > 0
                  ? "primary"
                  : "secondary"
            }
          >
            {readyCount} / {totalCount} {t("Ready")}
          </Badge>
          <ProgressBar
            now={percent}
            variant={percent === 100 ? "success" : percent > 50 ? "primary" : "warning"}
            style={{ width: "90px", height: "6px" }}
          />
        </div>
      );
    },
  },
  {
    header: t("Doctrines"),
    id: "doctrines",
    cell: ({ row }) => {
      const member = row.original;
      if (!member.isAudited) {
        return (
          <div className="d-flex align-items-center gap-2 py-1 text-muted small">
            <span
              className="spinner-border spinner-border-sm"
              style={{ width: "12px", height: "12px" }}
            />
            <span>{t("Evaluating doctrine skills...")}</span>
          </div>
        );
      }

      const memberDoctrines = activeDoctrines
        .map((d) => {
          const doc = member.doctrines?.[d.name] as DoctrineStatus | undefined;
          if (!doc) return null;
          const hasMissing = doc.skills && doc.skills.length > 0;
          return {
            ...doc,
            name: doc.name || d.name,
            id: doc.id || d.id,
            isReady: !hasMissing,
            missingCount: doc.skills ? doc.skills.length : 0,
          };
        })
        .filter(Boolean);

      if (memberDoctrines.length === 0) {
        return (
          <span className="text-muted small">
            {t("No doctrines in this category")}
          </span>
        );
      }

      return (
        <div className="d-flex flex-wrap gap-2 py-1">
          {memberDoctrines.map((doc) => {
            if (!doc) return null;
            if (doc.isReady) {
              return (
                <Badge
                  key={doc.name}
                  bg="success"
                  className="d-inline-flex align-items-center gap-1 py-1 px-2"
                  role="button"
                  style={{ cursor: "pointer" }}
                  onClick={() => doc.id && onOpenSkills(doc.id, member.character.character_id)}
                  title={t("Doctrine Ready - Click to view skills")}
                >
                  <CheckCircle2 size={13} />
                  <span>{doc.name}</span>
                  <span className="ms-1 small opacity-75">{t("Ready")}</span>
                </Badge>
              );
            }

            return (
              <Badge
                key={doc.name}
                bg="danger"
                className="d-inline-flex align-items-center gap-1 py-1 px-2"
                role="button"
                style={{ cursor: "pointer" }}
                onClick={() =>
                  doc.id &&
                  onOpenMissingSkills(member.character.character_id, doc.id)
                }
                title={t("Click to view missing skills")}
              >
                <AlertTriangle size={13} />
                <span>{doc.name}</span>
                <span className="ms-1 small opacity-75">
                  {t("Not Ready")} ({doc.missingCount})
                </span>
              </Badge>
            );
          })}
        </div>
      );
    },
  },
];
