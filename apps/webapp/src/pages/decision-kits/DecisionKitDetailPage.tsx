import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useDecisionKit } from '../../hooks/useDecisionKit';
import { useRubricSummary } from '../../hooks/useRubricSummary';
import { Box, Typography, Skeleton, Alert, Button, Grid, Card, CardContent, IconButton, Collapse, Divider, Stack, Snackbar, TextField } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/PersonAdd';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SaveIcon from '@mui/icons-material/Save';
import { useNavigate } from 'react-router-dom';
import { DeleteKitButton } from '../../components/decisionKits/DeleteKitButton';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { RubricCriteriaTable } from '../../components/RubricCriteriaTable';
import { AttachRubricForm } from '../../components/AttachRubricForm';
import { fetchRubricSummary } from '../../api/rubrics';
import { assignRubricToDecisionKit, updateDecisionKit } from '../../api/decisionKits';
import { evaluateCandidates } from '../../api/agent';

export const DecisionKitDetailPage: React.FC = () => {
  const { kitId } = useParams();
  const { kit, loading, error, retry, reload } = useDecisionKit(kitId || null);
  const rubricId = kit?.rubric?.id || kit?.rubricId;
  const needsRubricFetch = !kit?.rubric && !!rubricId;
  const { rubric, loading: rubricLoading, error: rubricError, retry: retryRubric } = useRubricSummary(needsRubricFetch ? rubricId : undefined);
  const [attachedRubric, setAttachedRubric] = useState<any | null>(null);
  const effectiveRubric = attachedRubric || kit?.rubric || rubric;
  const [rubricOpen, setRubricOpen] = useState(true);
  const [candidatesOpen, setCandidatesOpen] = useState(true);
  const [evaluatingId, setEvaluatingId] = useState<string | null>(null);
  const [toast, setToast] = useState<{ open: boolean; message: string; severity: 'success' | 'error' } | null>(null);
  const [editingName, setEditingName] = useState<string | null>(null);
  const [editingDescription, setEditingDescription] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [nameError, setNameError] = useState<string | null>(null);
  // const [attachError, setAttachError] = useState<string | null>(null);

  if (process.env.NODE_ENV !== 'production') {
    console.debug('[DecisionKitDetail] kitId', kitId, 'needsRubricFetch', needsRubricFetch, 'rubricId', rubricId);
  }

  const navigate = useNavigate();

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

  const currentRubricId = (effectiveRubric && (effectiveRubric as any).id) || rubricId;

  const nameValue = editingName !== null ? editingName : kit.name;
  const descriptionValue = editingDescription !== null ? editingDescription : (kit.description || '');

  // Validate name on change (length 3-60, allowed characters A-Za-z0-9 _-)
  const validateName = (val: string) => {
    const trimmed = val.trim();
    if (!trimmed) return 'Name is required';
    if (trimmed.length < 3 || trimmed.length > 60) return 'Name must be 3-60 characters';
    if (!/^[A-Za-z0-9 _-]+$/.test(trimmed)) return 'Only letters, numbers, spaces, underscore, and dash are allowed';
    return null;
  };

  return (
    <Box>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1, flexWrap: 'nowrap' }}>
        <Box sx={{ flexGrow: 1, minWidth: 0, mr: 1 }}>
          <TextField
            label="Decision Kit Name"
            value={nameValue}
            size="small"
            onChange={(e) => {
              const v = e.target.value;
              setEditingName(v);
              setNameError(validateName(v));
            }}
            fullWidth
            error={!!nameError}
            helperText={nameError || ''}
            FormHelperTextProps={{ sx: { minHeight: nameError ? undefined : 0, m: nameError ? '3px 14px 0 14px' : 0 } }}
          />
        </Box>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ flexShrink: 0 }}>
          <Button
            size="small"
            variant="contained"
            color="primary"
            startIcon={<SaveIcon />}
            disabled={saving || (editingName === null && editingDescription === null) || (!!nameError && editingName !== null)}
            onClick={async () => {
              try {
                setSaving(true);
                const payload: any = {};
                const nameTrim = editingName !== null ? editingName.trim() : null;
                const descTrim = editingDescription !== null ? editingDescription.trim() : null;
                if (editingName !== null) {
                  const err = validateName(nameTrim || '');
                  setNameError(err);
                  if (err) throw new Error(err);
                }
                if (editingName !== null && nameTrim !== kit.name) payload.name = nameTrim;
                if (editingDescription !== null && descTrim !== (kit.description || '')) payload.description = descTrim;
                if (Object.keys(payload).length === 0) {
                  setToast({ open: true, message: 'No changes to save', severity: 'error' });
                } else {
                  await updateDecisionKit(kit.id, payload);
                  // reset edit fields
                  setEditingName(null);
                  setEditingDescription(null);
                  setNameError(null);
                  // refresh the kit so UI reflects latest server data
                  await reload();
                  setToast({ open: true, message: 'Decision kit saved', severity: 'success' });
                }
              } catch (e: any) {
                const msg = e?.response?.data?.detail || e?.message || 'Failed to save';
                if (typeof msg === 'string' && msg.toLowerCase().includes('exists')) {
                  setNameError('A decision kit with this name already exists');
                }
                setToast({ open: true, message: msg, severity: 'error' });
              } finally {
                setSaving(false);
              }
            }}
          >
            Save
          </Button>
          <DeleteKitButton kitId={kit.id} kitName={kit.name} />
        </Stack>
      </Stack>
      <TextField
        label="Description"
        value={descriptionValue}
        onChange={(e) => setEditingDescription(e.target.value)}
        fullWidth
        multiline
        minRows={2}
        sx={{ mb: 3 }}
      />
      <Box sx={{ mb: 4 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>Rubric</Typography>
          <Stack direction="row" spacing={1} alignItems="center">
            {currentRubricId && (
              <Button
                size="small"
                variant="contained"
                startIcon={<EditIcon />}
                onClick={() => navigate(`/rubrics/${currentRubricId}/edit`, { state: { from: `/decision-kits/${kit.id}` } })}
              >
                Edit Rubric
              </Button>
            )}
            <IconButton aria-label={rubricOpen ? 'collapse rubric' : 'expand rubric'} size="small" onClick={() => setRubricOpen(o => !o)}>
              {rubricOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Stack>
        </Box>
        <Divider sx={{ mb: 1 }} />
        {rubricError && <Alert severity="error" action={<Button onClick={retryRubric}>Retry</Button>}>{rubricError}</Alert>}
        {!effectiveRubric && (rubricLoading ? (
          <>
            <Skeleton variant="text" width="30%" />
            <Skeleton variant="rectangular" height={60} sx={{ mt: 1 }} />
          </>
        ) : (
          <Box>
            <Typography variant="body2" sx={{ mb: 1 }}>No rubric data available. Attach one to get started.</Typography>
            <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
              <Button
                size="small"
                variant="contained"
                onClick={() => navigate('/rubrics/new', { state: { from: `/decision-kits/${kit.id}` } })}
              >
                Create Rubric
              </Button>
            </Stack>
            {kit && (
              <AttachRubricForm
                onAttach={async (rid: string) => {
                  const updated = await assignRubricToDecisionKit(kit.id, rid);
                  if (updated && (updated as any).rubric) {
                    setAttachedRubric((updated as any).rubric);
                  } else {
                    try {
                      const summary = await fetchRubricSummary(rid);
                      setAttachedRubric(summary as any);
                    } catch {
                      // ignore fetch errors here; leave UI as-is
                    }
                  }
                }}
              />
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
        <Box display="flex" alignItems="center" justifyContent="space-between" gap={2}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>Candidates ({kit.candidates.length})</Typography>
          <Stack direction="row" spacing={1} alignItems="center">
            <Button size="small" variant="contained" startIcon={<AddIcon />} onClick={() => navigate(`/decision-kits/${kit.id}/candidates/new`)}>Add Candidate</Button>
            <IconButton aria-label={candidatesOpen ? 'collapse candidates' : 'expand candidates'} size="small" onClick={() => setCandidatesOpen(o => !o)}>
              {candidatesOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Stack>
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
                    <CardContent sx={{ position: 'relative', pb: 4 }}>
                      <Typography variant="subtitle1" noWrap>{cd.name}</Typography>
                      {cd.description && <Typography variant="body2" className="twoLineClamp">{cd.description}</Typography>}
                      <IconButton
                        aria-label="edit candidate"
                        size="small"
                        sx={{ position: 'absolute', top: 4, right: 4 }}
                        onClick={() => navigate(`/decision-kits/${kit.id}/candidates/${cd.id}/edit`)}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<PlayArrowIcon />}
                          disabled={!currentRubricId || evaluatingId === cd.id}
                          onClick={async () => {
                            if (!currentRubricId) return;
                            try {
                              setEvaluatingId(cd.id);
                              const resp = await evaluateCandidates(String(currentRubricId), [String(cd.id)]);
                              if (resp.status === 'success') {
                                const msg = resp.evaluation_id ? `Evaluation started: ${resp.evaluation_id}` : 'Evaluation complete';
                                setToast({ open: true, message: msg, severity: 'success' });
                              } else {
                                setToast({ open: true, message: resp.error || 'Evaluation failed', severity: 'error' });
                              }
                            } catch (e: any) {
                              setToast({ open: true, message: e?.message || 'Evaluation error', severity: 'error' });
                            } finally {
                              setEvaluatingId(null);
                            }
                          }}
                        >
                          Evaluate
                        </Button>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
          </Grid>
        </Collapse>
      </Box>
      <Snackbar
        open={!!toast?.open}
        autoHideDuration={4000}
        onClose={() => setToast(t => t ? { ...t, open: false } : t)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        message={toast?.message}
      />
    </Box>
  );
};
