import React, { useState } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import { useDecisionKit } from '../../hooks/useDecisionKit';
import { useRubricSummary } from '../../hooks/useRubricSummary';
import { Box, Typography, Skeleton, Alert, Button, Grid, Card, CardContent, IconButton, Collapse, Divider, Fab } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { RubricCriteriaTable } from '../../components/RubricCriteriaTable';
// import { assignRubricToDecisionKit, primeDecisionKitCache } from '../../api/decisionKits';

export const DecisionKitDetailPage: React.FC = () => {
  const { kitId } = useParams();
  const { kit, loading, error, retry } = useDecisionKit(kitId || null);
  const rubricId = kit?.rubric?.id || kit?.rubricId;
  const needsRubricFetch = !kit?.rubric && !!rubricId;
  const { rubric, loading: rubricLoading, error: rubricError, retry: retryRubric } = useRubricSummary(needsRubricFetch ? rubricId : undefined);
  const effectiveRubric = kit?.rubric || rubric;
  const [rubricOpen, setRubricOpen] = useState(true);
  const [candidatesOpen, setCandidatesOpen] = useState(true);
  // const [attachError, setAttachError] = useState<string | null>(null);

  if (process.env.NODE_ENV !== 'production') {
    console.debug('[DecisionKitDetail] kitId', kitId, 'needsRubricFetch', needsRubricFetch, 'rubricId', rubricId);
  }

  if (error) return <Alert severity="error" action={<Button onClick={retry}>Retry</Button>}>{error}</Alert>;

  if (loading || !kit) {
    return (
      <Box>
        <Skeleton variant="text" width="40%" />
        <Skeleton variant="text" width="60%" />
        <Skeleton variant="rectangular" height={80} sx={{ mt: 2 }} />
      </Box>
    );
  }

  // Map backend criteria entries (criteriaId) to table expected shape (criteria_id)
  const tableCriteria = (effectiveRubric?.criteria || []).map((c: any) => ({
    criteria_id: c.criteria_id ?? c.criteriaId,
    name: c.name,
    weight: c.weight,
    description: c.description,
    definition: c.definition
  }));

  return (
    <Box>
      <Typography variant="h4" gutterBottom>{kit.name}</Typography>
      {kit.description && <Typography variant="body1" sx={{ mb: 3 }}>{kit.description}</Typography>}
      <Box sx={{ mb: 4 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>Rubric</Typography>
          <IconButton aria-label={rubricOpen ? 'collapse rubric' : 'expand rubric'} size="small" onClick={() => setRubricOpen(o => !o)}>
            {rubricOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
        <Divider sx={{ mb: 1 }} />
        {rubricError && <Alert severity="error" action={<Button onClick={retryRubric}>Retry</Button>}>{rubricError}</Alert>}
        {!effectiveRubric && (rubricLoading ? (
          <>
            <Skeleton variant="text" width="30%" />
            <Skeleton variant="rectangular" height={60} sx={{ mt: 1 }} />
          </>
        ) : (
          <Box position="relative">
            <Typography variant="body2" sx={{ mb: 1 }}>No rubric data available.</Typography>
            {/* Error display removed with inline attach; rely on attach page for errors */}
            {kit && (
              <Fab
                color="primary"
                variant="extended"
                aria-label="Attach Rubric"
                component={RouterLink}
                to={`/decision-kits/${encodeURIComponent(kit.id)}/attach-rubric`}
                sx={{ position: 'fixed', bottom: 24, right: 24, zIndex: (theme) => theme.zIndex.tooltip }}
              >
                <AddIcon sx={{ mr: 1 }} /> Attach Rubric
              </Fab>
            )}
          </Box>
        ))}
        <Collapse in={rubricOpen} unmountOnExit timeout="auto">
          {effectiveRubric && (
            <>
              <Typography variant="subtitle1" sx={{ mt: 1 }}>{effectiveRubric.name}</Typography>
              {effectiveRubric.description && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>{effectiveRubric.description}</Typography>
              )}
              <Typography variant="body2" sx={{ mb: 1 }}>Criteria: {effectiveRubric.criteria.length}</Typography>
              {effectiveRubric.criteria.length > 0 ? (
                <RubricCriteriaTable criteria={tableCriteria} />
              ) : (
                <Typography variant="caption" color="text.secondary">No criteria defined for this rubric.</Typography>
              )}
            </>
          )}
        </Collapse>
      </Box>
      <Box>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>Candidates ({kit.candidates.length})</Typography>
          <IconButton aria-label={candidatesOpen ? 'collapse candidates' : 'expand candidates'} size="small" onClick={() => setCandidatesOpen(o => !o)}>
            {candidatesOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
        <Divider sx={{ mb: 1 }} />
        <Collapse in={candidatesOpen} unmountOnExit timeout="auto">
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {kit.candidates
              .map((cd: any) => ({
                id: cd.candidateId || cd.id,
                name: cd.candidateName || cd.name,
                description: cd.description,
                position: cd.position ?? 0,
              }))
              .sort((a: any, b: any) => a.position - b.position)
              .map((cd: any) => (
                <Grid item xs={12} sm={6} md={4} key={cd.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" noWrap>{cd.name}</Typography>
                      {cd.description && <Typography variant="body2" className="twoLineClamp">{cd.description}</Typography>}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
          </Grid>
        </Collapse>
      </Box>
    </Box>
  );
};
