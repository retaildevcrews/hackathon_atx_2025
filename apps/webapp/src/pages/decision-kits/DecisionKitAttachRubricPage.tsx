import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Box, Typography, Alert } from '@mui/material';
import { AttachRubricForm } from '../../components/AttachRubricForm';
import { assignRubricToDecisionKit } from '../../api/decisionKits';

export const DecisionKitAttachRubricPage: React.FC = () => {
  const { kitId } = useParams();
  const navigate = useNavigate();
  const [error, setError] = React.useState<string | null>(null);

  if (!kitId) {
    return <Alert severity="error">Missing decision kit id.</Alert>;
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Attach a Rubric to Decision Kit</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Enter a rubric ID to attach it to this decision kit.
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <AttachRubricForm
        onAttach={async (rubricId: string) => {
          setError(null);
          try {
            await assignRubricToDecisionKit(kitId, rubricId);
            navigate(`/decision-kits/${encodeURIComponent(kitId)}`);
          } catch (e: any) {
            setError(e?.message || 'Failed to attach rubric.');
          }
        }}
      />
    </Box>
  );
};
