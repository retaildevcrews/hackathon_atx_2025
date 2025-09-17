import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { Box, Typography, CircularProgress, Alert } from '@mui/material';
import { fetchCandidate } from '../../api/candidates';
import { CandidateForm } from '../../components/candidates/CandidateForm';
import { useUpdateCandidate } from '../../hooks/useUpdateCandidate';

export const EditCandidatePage: React.FC = () => {
  const { candidateId, kitId } = useParams();
  const location = useLocation();
  const resolvedKitId = kitId || (location.state as any)?.kitId || new URLSearchParams(location.search).get('kitId') || '';
  const navigate = useNavigate();
  const { update, updating, error } = useUpdateCandidate(candidateId || null);
  const [loading, setLoading] = useState(true);
  const [initial, setInitial] = useState<{ name: string; description: string }>({ name: '', description: '' });
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!candidateId) return;
      try {
        const c = await fetchCandidate(candidateId);
        if (!cancelled) {
          setInitial({ name: c.name, description: c.description || '' });
        }
      } catch (e: any) {
        if (!cancelled) setLoadError(e?.message || 'Failed to load candidate');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [candidateId]);

  async function handleSubmit(values: { name: string; description: string }) {
    const updated = await update({ name: values.name, description: values.description, decisionKitId: resolvedKitId });
    if (updated) {
      navigate(resolvedKitId ? `/decision-kits/${resolvedKitId}` : '/');
    }
  }

  return (
    <Box maxWidth="md" mx="auto">
      <Typography variant="h4" gutterBottom>Edit Candidate</Typography>
      {loading && <CircularProgress />}
      {loadError && <Alert severity="error" sx={{ mb: 2 }}>{loadError}</Alert>}
      {!loading && !loadError && (
        <CandidateForm
          mode="edit"
          initial={initial}
          submitting={updating}
          error={error}
          onSubmit={handleSubmit}
          onCancel={() => navigate(resolvedKitId ? `/decision-kits/${resolvedKitId}` : '/')}
        />
      )}
    </Box>
  );
};

export default EditCandidatePage;
