import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './layout/AppLayout';
import { DecisionKitListPage } from './decision-kits/DecisionKitListPage';
import { DecisionKitDetailPage } from './decision-kits/DecisionKitDetailPage';
import { AddDecisionKitPage } from './decision-kits/AddDecisionKitPage';

export const App: React.FC = () => {
  const enableDecisionKits =
    typeof window !== 'undefined'
      ? (window as any).__ENABLE_DECISION_KITS_UI__ !== 'false'
      : true;

  if (!enableDecisionKits) {
    // Render legacy rubric UI (used by some integration tests)
    return <LegacyRubricApp />;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<DecisionKitListPage />} />
          <Route path="decision-kits/new" element={<AddDecisionKitPage />} />
          <Route path="decision-kits/:kitId" element={<DecisionKitDetailPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
