// React
import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

// Third Party
import { QueryClientProvider } from "@tanstack/react-query";
import { AaReactProvider, AuthBase, createQueryClient, ErrorPage } from "aa-geuthur-react";
import { NuqsAdapter } from "nuqs/adapters/react-router/v8";

// AA Memberaudit Doctrine Checker
import { AppName, ProjectName } from "@/constants";
import CorporationDoctrinesPage from "@/Pages/CorporationDoctrinesPage";
import DoctrinesPage from "@/Pages/DoctrinesPage";
import MainPage from "@/Pages/MainPage";
import ManagePage from "@/Pages/ManagePage";
import OverviewPage from "@/Pages/OverviewPage";

const queryClient = createQueryClient();

function Routing() {
  return (
    <React.StrictMode>
      <AaReactProvider projectName={ProjectName} appName={AppName}>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <NuqsAdapter>
              <Routes>
                <Route path={`/${ProjectName}/`} element={<AuthBase fluidOnSmallScreens />}>
                  <Route index element={<MainPage />} />
                  <Route path="doctrine/" element={<DoctrinesPage />} />
                  <Route path="doctrine/:characterId/" element={<DoctrinesPage />} />
                  <Route path="corporation/" element={<CorporationDoctrinesPage />} />
                  <Route
                    path="corporation/:corporationId/"
                    element={<CorporationDoctrinesPage />}
                  />
                  <Route path="overview/" element={<OverviewPage />} />
                  <Route path="manage/" element={<ManagePage />} />
                  <Route path="*" element={<ErrorPage />} />
                </Route>
                <Route path="*" element={<Navigate to={`/${ProjectName}/`} replace />} />
              </Routes>
            </NuqsAdapter>
          </BrowserRouter>
        </QueryClientProvider>
      </AaReactProvider>
    </React.StrictMode>
  );
}

export default Routing;
