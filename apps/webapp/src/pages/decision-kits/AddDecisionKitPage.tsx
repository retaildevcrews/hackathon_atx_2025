import React, { useState } from 'react';
import { Box, Typography, Snackbar, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { DecisionKitForm } from '../../components/decisionKits/DecisionKitForm';
import { useCreateDecisionKit } from '../../hooks/useCreateDecisionKit';
import { useDecisionKits } from '../../hooks/useDecisionKits';
import { useRubrics } from '../../hooks/useRubrics';

export const AddDecisionKitPage: React.FC = () => {
  const navigate = useNavigate();
  const { kits, addKit } = useDecisionKits();
  const { rubrics, loading: rubricsLoading, error: rubricsError } = useRubrics();
  const [toastOpen, setToastOpen] = useState(false);
  const { createDecisionKit, loading, error } = useCreateDecisionKit({
    getList: () => kits,
  setList: () => {/* intentionally unused; we rely on addKit */},
    onSuccess: (kit) => {
      addKit(kit);
      setToastOpen(true);
      navigate(`/decision-kits/${kit.id}`);
    }
  });

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Create Decision Kit</Typography>
      {(!rubricsLoading && rubrics && rubrics.length === 0) && (
        <Alert severity="info" sx={{ mb: 2 }}>
          No rubrics available. Create a rubric first before creating a decision kit.
        </Alert>
      )}
      <DecisionKitForm
        loading={loading}
        error={error || rubricsError || undefined}
        rubrics={(rubrics || []).map(r => ({ id: r.id, name: r.name }))}
        rubricsLoading={rubricsLoading}
        onSubmit={(values) => createDecisionKit(values)}
        onCancel={() => navigate(-1)}
      />
      <Snackbar open={toastOpen} autoHideDuration={3000} onClose={() => setToastOpen(false)} message={undefined}>
        <Alert severity="success" variant="filled" sx={{ width: '100%' }}>Decision kit created</Alert>
      </Snackbar>
    </Box>
  );
};
