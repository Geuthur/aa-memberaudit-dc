// React
import React, { useMemo } from "react";

// Third Party
import { BaseTable } from "aa-geuthur-react";
import { useTranslation } from "react-i18next";

// AA Memberaudit Doctrine Checker
import type { ActiveDoctrineOverview } from "@/Api/schema";
import type { MemberDoctrineRow } from "@/Components/Corporation/types";
import { getCorporationMatrixColumns } from "@/Components/Tables";

export interface CorporationMatrixTableProps {
  members: MemberDoctrineRow[];
  activeDoctrines: ActiveDoctrineOverview[];
  onOpenSkills: (doctrineId: number, characterId?: number) => void;
  onOpenMissingSkills: (charId: number, doctrineId: number) => void;
}

export const CorporationMatrixTable: React.FC<CorporationMatrixTableProps> = ({
  members,
  activeDoctrines,
  onOpenSkills,
  onOpenMissingSkills,
}) => {
  const { t } = useTranslation();

  const columns = useMemo(
    () =>
      getCorporationMatrixColumns(
        t,
        activeDoctrines,
        onOpenSkills,
        onOpenMissingSkills
      ),
    [activeDoctrines, t, onOpenSkills, onOpenMissingSkills]
  );

  return (
    <BaseTable
      columns={columns}
      data={members}
      striped
      hover
      className="madc-matrix"
      tableClassName="aa-table-sticky-header aa-table-sticky-first-col"
    />
  );
};

export default CorporationMatrixTable;
