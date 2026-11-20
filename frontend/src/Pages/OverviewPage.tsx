// React
import React, { useState } from "react";

// Third Party
import { useQuery } from "@tanstack/react-query";
import { useUserData } from "aa-geuthur-react";
import { Card } from "react-bootstrap";

// AA Memberaudit Doctrine Checker
import { loadAccountOverview, loadCorporationOverview } from "@/Api/ApiCalls";
import { queryKeys } from "@/Api/query";
import type { UserData } from "@/Api/schema";
import {
  AccountOverviewTable,
  CorporationOverviewTable,
  OverviewNav,
} from "@/Components/Overview";

export const OverviewPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"account" | "corporation">("account");

  const { data: userData } = useUserData<UserData>();

  const {
    data: accountData,
    isLoading: isLoadingAccount,
    isError: isErrorAccount,
  } = useQuery({
    queryKey: queryKeys.AccountOverview,
    queryFn: loadAccountOverview,
  });

  const canViewCorp = Boolean(
    userData?.user.permissions?.corp_access ||
      userData?.user.permissions?.alliance_access ||
      userData?.user.is_admin
  );

  const {
    data: corpData,
    isLoading: isLoadingCorp,
    isError: isErrorCorp,
  } = useQuery({
    queryKey: queryKeys.CorporationOverview,
    queryFn: loadCorporationOverview,
    enabled: canViewCorp,
  });

  return (
    <main>
      <OverviewNav
        activeTab={activeTab}
        onTabChange={setActiveTab}
        accountCount={accountData?.length}
        corpCount={corpData?.length}
        canViewCorp={canViewCorp}
      />

      <Card className="border-0 shadow-sm aa-panel">
        <Card.Body className="p-3">
          {activeTab === "account" ? (
            <AccountOverviewTable
              data={accountData || []}
              isLoading={isLoadingAccount}
              isError={isErrorAccount}
            />
          ) : (
            <CorporationOverviewTable
              data={corpData || []}
              isLoading={isLoadingCorp}
              isError={isErrorCorp}
            />
          )}
        </Card.Body>
      </Card>
    </main>
  );
};

export default OverviewPage;
