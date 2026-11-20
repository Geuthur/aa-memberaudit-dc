// React
import React, { useMemo } from "react";

// Third Party
import { BaseTable } from "aa-geuthur-react";
import { useTranslation } from "react-i18next";

// AA Memberaudit Doctrine Checker
import type { ActiveDoctrineOverview } from "@/Api/schema";
import type { MemberDoctrineRow } from "@/Components/Corporation/types";
import { getCorporationBadgesColumns } from "@/Components/Tables";

export interface CorporationBadgesTableProps {
  members: MemberDoctrineRow[];
  activeDoctrines: ActiveDoctrineOverview[];
  onOpenSkills: (doctrineId: number, characterId?: number) => void;
  onOpenMissingSkills: (charId: number, doctrineId: number) => void;
}

export const CorporationBadgesTable: React.FC<CorporationBadgesTableProps> = ({
  members,
  activeDoctrines,
  onOpenSkills,
  onOpenMissingSkills,
}) => {
  const { t } = useTranslation();

  const columns = useMemo(
    () =>
      getCorporationBadgesColumns(
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
    />
  );
};

export default CorporationBadgesTable;
