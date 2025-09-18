import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './layout/AppLayout';
import { LegacyRubricApp } from './LegacyRubricApp';

// Lazy loaded route components
const DecisionKitListPage = lazy(() => import('./decision-kits/DecisionKitListPage').then(m => ({ default: m.DecisionKitListPage })));
const DecisionKitDetailPage = lazy(() => import('./decision-kits/DecisionKitDetailPage').then(m => ({ default: m.DecisionKitDetailPage })));
const AddDecisionKitPage = lazy(() => import('./decision-kits/AddDecisionKitPage').then(m => ({ default: m.AddDecisionKitPage })));
const RubricsListPage = lazy(() => import('./rubrics/RubricsListPage').then(m => ({ default: m.RubricsListPage })));
const RubricDetailPage = lazy(() => import('./rubrics/RubricDetailPage').then(m => ({ default: m.RubricDetailPage })));
const AddEditRubricPage = lazy(() => import('./rubrics/AddEditRubricPage').then(m => ({ default: m.AddEditRubricPage })));
const CreateCandidatePage = lazy(() => import('./candidates/CreateCandidatePage').then(m => ({ default: m.CreateCandidatePage })));
const EditCandidateMaterialsPage = lazy(() => import('./candidates/EditCandidateMaterialsPage').then(m => ({ default: m.EditCandidateMaterialsPage })));
const EditCandidatePage = lazy(() => import('./candidates/EditCandidatePage').then(m => ({ default: m.EditCandidatePage })));
const CandidateLatestEvaluationPage = lazy(() => import('./candidates/CandidateLatestEvaluationPage').then(m => ({ default: m.CandidateLatestEvaluationPage })));

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
      <Suspense fallback={<div style={{ padding: '1rem' }}>Loading...</div>}>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<DecisionKitListPage />} />

            {/* Decision Kit Routes */}
            <Route path="decision-kits/new" element={<AddDecisionKitPage />} />
            <Route path="decision-kits/:kitId" element={<DecisionKitDetailPage />} />
            <Route path="decision-kits/:kitId/candidates/new" element={<CreateCandidatePage />} />
            <Route path="decision-kits/:kitId/candidates/:candidateId/edit" element={<EditCandidatePage />} />
            <Route path="decision-kits/:kitId/candidates/:candidateId/evaluations/latest" element={<CandidateLatestEvaluationPage />} />
            {/* Existing materials edit route left intact temporarily if used elsewhere */}
            <Route path="candidates/:candidateId/edit" element={<EditCandidateMaterialsPage />} />

            {/* Rubric Routes */}
            <Route path="rubrics" element={<RubricsListPage />} />
            <Route path="rubrics/new" element={<AddEditRubricPage />} />
            <Route path="rubrics/:id" element={<RubricDetailPage />} />
            <Route path="rubrics/:id/edit" element={<AddEditRubricPage />} />

            {/* Catch-all redirect */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
};
