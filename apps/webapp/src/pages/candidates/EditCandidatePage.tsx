import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { Box, Typography, CircularProgress, Alert, Divider, Button, Stack } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { fetchCandidate } from '../../api/candidates';
import { CandidateForm } from '../../components/candidates/CandidateForm';
import { useUpdateCandidate } from '../../hooks/useUpdateCandidate';
import { EditCandidateMaterialsPage } from './EditCandidateMaterialsPage';

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
    await update({ name: values.name, description: values.description, decisionKitId: resolvedKitId });
    // Stay on page so user can continue managing materials
  }

  return (
    <Box maxWidth="lg" mx="auto">
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(resolvedKitId ? `/decision-kits/${resolvedKitId}` : '/')}
          variant="text"
        >Back to Decision Kit</Button>
        <Typography variant="h4" gutterBottom sx={{ ml: 1 }}>Edit Candidate</Typography>
      </Stack>
      {loading && <CircularProgress />}
      {loadError && <Alert severity="error" sx={{ mb: 2 }}>{loadError}</Alert>}
      {!loading && !loadError && (
        <>
          <CandidateForm
            mode="edit"
            initial={initial}
            submitting={updating}
            error={error}
            onSubmit={handleSubmit}
            onCancel={() => navigate(resolvedKitId ? `/decision-kits/${resolvedKitId}` : '/')}
          />
          <Divider sx={{ my: 4 }} />
          <Typography variant="h5" gutterBottom>Materials</Typography>
          <EditCandidateMaterialsPage embedded />
        </>
      )}
    </Box>
  );
};

export default EditCandidatePage;
