import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import { Box, Button, Alert, Skeleton, Typography, Stack } from '@mui/material';
import { useCandidateEvaluations } from '../../hooks/useCandidateEvaluations';
import { fetchEvaluationResult } from '../../api/evaluations';
import { EvaluationResult } from '../../types/evaluations';
import { CandidateEvaluationDetail } from '../../components/evaluations/CandidateEvaluationDetail';

export const CandidateLatestEvaluationPage: React.FC = () => {
  const { kitId, candidateId } = useParams();
  const navigate = useNavigate();
  const { latest, loading: summaryLoading, error: summaryError, retry: retrySummaries, refresh } = useCandidateEvaluations(candidateId);
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  const loadDetail = useCallback(async (evalId: string) => {
    setDetailLoading(true);
    setDetailError(null);
    try {
      const full = await fetchEvaluationResult(evalId);
      setEvaluation(full);
    } catch (e: any) {
      setDetailError(e?.message || 'Failed to load evaluation');
    } finally {
      setDetailLoading(false);
    }
  }, []);

  useEffect(() => {
    if (latest) loadDetail(latest.id);
  }, [latest, loadDetail]);

  const back = () => navigate(`/decision-kits/${kitId}`);

  return (
    <Box>
      <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
        <Button variant="outlined" onClick={back}>Back to Decision Kit</Button>
        <Button variant="text" component={RouterLink} to={`/decision-kits/${kitId}`}>
          Kit Overview
        </Button>
      </Stack>
      <Typography variant="h5" sx={{ mb: 2 }}>Latest Evaluation</Typography>
      {summaryError && (
        <Alert severity="error" action={<Button onClick={retrySummaries}>Retry</Button>} sx={{ mb: 2 }}>{summaryError}</Alert>
      )}
      {summaryLoading && !latest && (
        <Box sx={{ mb: 2 }}>
          <Skeleton variant="text" width={240} />
          <Skeleton variant="rectangular" height={120} />
        </Box>
      )}
      {!summaryLoading && !latest && !summaryError && (
        <Alert severity="info" sx={{ mb: 2 }}>
          No evaluations found for this candidate yet. Run an evaluation from the decision kit page.
        </Alert>
      )}
      {latest && detailLoading && (
        <Skeleton variant="rectangular" height={160} sx={{ mb: 2 }} />
      )}
      {detailError && (
        <Alert severity="error" action={<Button onClick={() => latest && loadDetail(latest.id)}>Retry</Button>} sx={{ mb: 2 }}>{detailError}</Alert>
      )}
      {evaluation && !detailLoading && !detailError && (
        <CandidateEvaluationDetail evaluation={evaluation} candidateId={candidateId!} />
      )}
      <Box sx={{ mt: 3 }}>
        <Button size="small" onClick={refresh}>Refresh</Button>
      </Box>
    </Box>
  );
};
