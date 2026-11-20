// React
import React, { useMemo } from "react";

// Third Party
import { BaseTable } from "aa-geuthur-react";
import { useTranslation } from "react-i18next";

// AA Memberaudit Doctrine Checker
import type { ManageSkillListSchema, SkillListUpdateRequest } from "@/Api/schema";
import { getManageDoctrinesColumns } from "@/Components/Tables";

export interface ManageDoctrinesTableProps {
  data: ManageSkillListSchema[];
  isLoading: boolean;
  isError: boolean;
  isDeleting: boolean;
  isUpdating: boolean;
  onEdit: (doctrine: ManageSkillListSchema) => void;
  onDelete: (doctrine: ManageSkillListSchema) => void;
  onViewSkills: (doctrineId: number) => void;
  onUpdate: (doctrineId: number, payload: SkillListUpdateRequest) => void;
}

export const ManageDoctrinesTable: React.FC<ManageDoctrinesTableProps> = ({
  data,
  isLoading,
  isError,
  isDeleting,
  isUpdating,
  onEdit,
  onDelete,
  onViewSkills,
  onUpdate,
}) => {
  const { t } = useTranslation();

  const columns = useMemo(
    () =>
      getManageDoctrinesColumns(
        t,
        isDeleting,
        isUpdating,
        onEdit,
        onDelete,
        onViewSkills,
        onUpdate
      ),
    [t, isDeleting, isUpdating, onEdit, onDelete, onViewSkills, onUpdate]
  );

  return (
    <BaseTable
      columns={columns}
      data={data}
      isFetching={isLoading}
      isError={isError}
      striped
      hover
    />
  );
};

export default ManageDoctrinesTable;
