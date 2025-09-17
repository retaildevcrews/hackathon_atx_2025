import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Box, Typography } from '@mui/material';
import { useCreateCandidate } from '../../hooks/useCreateCandidate';
import { CandidateForm } from '../../components/candidates/CandidateForm';

export const CreateCandidatePage: React.FC = () => {
  const { kitId } = useParams();
  const navigate = useNavigate();
  const { create, creating, error } = useCreateCandidate();

  async function handleSubmit(values: { name: string; description: string }) {
    if (!kitId) return;
    const candidate = await create({ name: values.name, description: values.description, decisionKitId: kitId });
    if (candidate) {
  navigate(`/decision-kits/${kitId}/candidates/${candidate.id}/edit`, { state: { kitId } });
    }
  }

  return (
    <Box maxWidth="md" mx="auto">
      <Typography variant="h4" gutterBottom>New Candidate</Typography>
      <CandidateForm
        mode="create"
        submitting={creating}
        error={error}
        onSubmit={handleSubmit}
        onCancel={() => navigate(kitId ? `/decision-kits/${kitId}` : '/')}
      />
    </Box>
  );
};
