import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './layout/AppLayout';
import { DecisionKitListPage } from './decision-kits/DecisionKitListPage';
import { DecisionKitDetailPage } from './decision-kits/DecisionKitDetailPage';
import { AddDecisionKitPage } from './decision-kits/AddDecisionKitPage';
import { RubricsListPage, RubricDetailPage, AddEditRubricPage } from './rubrics';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<DecisionKitListPage />} />

          {/* Decision Kit Routes */}
          <Route path="decision-kits/new" element={<AddDecisionKitPage />} />
          <Route path="decision-kits/:kitId" element={<DecisionKitDetailPage />} />

          {/* Rubric Routes */}
          <Route path="rubrics" element={<RubricsListPage />} />
          <Route path="rubrics/new" element={<AddEditRubricPage />} />
          <Route path="rubrics/:id" element={<RubricDetailPage />} />
          <Route path="rubrics/:id/edit" element={<AddEditRubricPage />} />

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
