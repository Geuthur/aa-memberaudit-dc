// React
import { Link } from "react-router-dom";

// Third Party
import type { BaseColumnDef } from "aa-geuthur-react";
import type { TFunction } from "i18next";
import { ExternalLink } from "lucide-react";

// AA Memberaudit Doctrine Checker
import type { CorporationOverviewSchema } from "@/Api/schema";
import { ProjectName } from "@/constants";

export const getCorporationOverviewColumns = (
  t: TFunction
): BaseColumnDef<CorporationOverviewSchema>[] => [
  {
    id: "corporation",
    header: () => t("Corporation"),
    accessorKey: "corporation_name",
    cell: ({ row }) => (
      <div className="d-flex align-items-center gap-2">
        <img
          src={`https://images.evetech.net/corporations/${row.original.corporation_id}/logo?size=32`}
          alt={row.original.corporation_name}
          className="rounded"
          width={30}
          height={30}
        />
        <span className="fw-semibold">{row.original.corporation_name}</span>
      </div>
    ),
  },
  {
    id: "alliance",
    header: () => t("Alliance"),
    accessorKey: "alliance_name",
    cell: ({ row }) => row.original.alliance_name || "-",
  },
  {
    id: "actions",
    header: () => t("Actions"),
    cell: ({ row }) => (
      <Link
        to={`/${ProjectName}/corporation/${row.original.corporation_id}/`}
        className="aa-btn aa-btn-sm aa-btn-primary"
      >
        <ExternalLink size={14} />
        <span>{t("View Overview")}</span>
      </Link>
    ),
  },
];
