// React
import React, { useMemo } from "react";

// Third Party
import { BaseTable } from "aa-geuthur-react";
import { useTranslation } from "react-i18next";

// AA Memberaudit Doctrine Checker
import type { CharacterOverviewSchema } from "@/Api/schema";
import { getAccountOverviewColumns } from "@/Components/Tables";

export interface AccountOverviewTableProps {
  data: CharacterOverviewSchema[];
  isLoading: boolean;
  isError: boolean;
}

export const AccountOverviewTable: React.FC<AccountOverviewTableProps> = ({
  data,
  isLoading,
  isError,
}) => {
  const { t } = useTranslation();

  const columns = useMemo(
    () => getAccountOverviewColumns(t),
    [t]
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

export default AccountOverviewTable;
