import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './layout/AppLayout';
import { DecisionKitListPage } from './decision-kits/DecisionKitListPage';
import { DecisionKitDetailPage } from './decision-kits/DecisionKitDetailPage';
import { DecisionKitAttachRubricPage } from './decision-kits/DecisionKitAttachRubricPage';
import { CreateRubricPage } from './decision-kits/CreateRubricPage';
import { LegacyRubricApp } from './LegacyRubricApp';

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
          <Route path="decision-kits/:kitId" element={<DecisionKitDetailPage />} />
          <Route path="decision-kits/:kitId/attach-rubric" element={<DecisionKitAttachRubricPage />} />
          <Route path="decision-kits/:kitId/create-rubric" element={<CreateRubricPage />} />
          <Route path="create-rubric" element={<CreateRubricPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
