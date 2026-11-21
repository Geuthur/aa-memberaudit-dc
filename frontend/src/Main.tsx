// React
import React from 'react'
import ReactDOM from "react-dom/client";

// Third Party
import { initI18n } from "aa-geuthur-react";

// AA Memberaudit Doctrine Checker
import { AppName, ProjectName } from '@/constants';
import Routing from '@/Routing';

// Styles
import '@/Styles/index.css';

initI18n(ProjectName, `${AppName}-root`);

const container = typeof document !== "undefined" ? document.getElementById(`${AppName}-root`) : null;

if (container) {
  ReactDOM.createRoot(container).render(
    <React.StrictMode>
      <Routing />
    </React.StrictMode>,
  );
}
