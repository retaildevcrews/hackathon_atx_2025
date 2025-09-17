import React, { useCallback, useRef, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Box, Typography, Alert, Button, Grid, Card, CardContent, CardActions, IconButton, LinearProgress, Stack } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import UploadIcon from '@mui/icons-material/CloudUpload';
import RefreshIcon from '@mui/icons-material/Refresh';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useCandidate } from '../../hooks/useCandidate';
import { useCandidateMaterials } from '../../hooks/useCandidateMaterials';
import { useUploadCandidateMaterial, useDeleteCandidateMaterial } from '../../hooks/useCandidateMaterialOps';

interface DraftItem { id: string; file: File; status: 'pending' | 'uploading' | 'error'; error?: string; }

export const EditCandidateMaterialsPage: React.FC = () => {
  const { candidateId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { candidate, loading: candidateLoading, error: candidateError } = useCandidate(candidateId || null);
  const { materials, loading: materialsLoading, error: materialsError, refresh } = useCandidateMaterials(candidateId || null);
  const { upload } = useUploadCandidateMaterial(candidateId || null);
  const { remove, deletingIds } = useDeleteCandidateMaterial(candidateId || null);
  const [drafts, setDrafts] = useState<DraftItem[]>([]);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const onFiles = useCallback((files: FileList | null) => {
    if (!files) return;
    const next: DraftItem[] = [];
    const existingNames = new Set([...materials.map(m => m.name.toLowerCase()), ...drafts.map(d => d.file.name.toLowerCase())]);
    Array.from(files).forEach(f => {
      if (existingNames.has(f.name.toLowerCase())) {
        next.push({ id: `${f.name}-${f.size}-${f.lastModified}`, file: f, status: 'error', error: 'Duplicate filename' });
      } else {
        next.push({ id: `${f.name}-${f.size}-${f.lastModified}`, file: f, status: 'pending' });
      }
    });
    setDrafts(d => [...d, ...next]);
  }, [materials, drafts]);

  const triggerFileDialog = () => fileInputRef.current?.click();

  const startUpload = async (draftId: string) => {
    setDrafts(ds => ds.map(d => d.id === draftId ? { ...d, status: 'uploading', error: undefined } : d));
    const draft = drafts.find(d => d.id === draftId);
    if (!draft) return;
    const result = await upload(draft.file);
    if (result) {
      // refresh remote list and remove draft
      setDrafts(ds => ds.filter(d => d.id !== draftId));
      refresh();
    } else {
      setDrafts(ds => ds.map(d => d.id === draftId ? { ...d, status: 'error', error: 'Upload failed' } : d));
    }
  };

  const startAllPending = async () => {
    for (const d of drafts) {
      if (d.status === 'pending') await startUpload(d.id);
    }
  };

  const deleteMaterial = async (materialId: string) => {
    const success = await remove(materialId);
    if (success) refresh();
  };

  return (
    <Box>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => {
            // Try to obtain kitId from nav state then query param
            const stateKitId = (location.state as any)?.kitId;
            const searchParams = new URLSearchParams(location.search);
            const queryKitId = searchParams.get('kitId');
            const targetKitId = stateKitId || queryKitId;
            navigate(targetKitId ? `/decision-kits/${targetKitId}` : '/');
          }}
          variant="text"
        >Back to Decision Kit</Button>
      </Stack>
      {candidateError && <Alert severity="error" sx={{ mb: 2 }}>{candidateError}</Alert>}
      {candidateLoading && <Typography>Loading candidate...</Typography>}
      {candidate && <Typography variant="h4" gutterBottom>Materials for: {candidate.name}</Typography>}
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 2 }}>
        <Button variant="contained" startIcon={<UploadIcon />} onClick={triggerFileDialog}>Add Files</Button>
        <Button variant="outlined" disabled={!drafts.some(d => d.status === 'pending')} onClick={startAllPending}>Upload All</Button>
        <Button variant="text" startIcon={<RefreshIcon />} onClick={() => refresh()} disabled={materialsLoading}>Refresh</Button>
      </Stack>
      <input ref={fileInputRef} type="file" multiple hidden onChange={e => onFiles(e.target.files)} />
      {materialsError && <Alert severity="error" sx={{ mb: 2 }}>{materialsError}</Alert>}
      <Grid container spacing={2}>
        {materials.map(m => (
          <Grid item xs={6} sm={4} md={3} key={m.id}>
            <Card variant="outlined" sx={{ position: 'relative' }}>
              <CardContent>
                <Typography variant="subtitle2" noWrap>{m.name}</Typography>
              </CardContent>
              {deletingIds.has(m.id) && <LinearProgress sx={{ position: 'absolute', bottom: 0, left: 0, right: 0 }} />}
              <CardActions sx={{ justifyContent: 'flex-end' }}>
                <IconButton aria-label="delete" size="small" onClick={() => deleteMaterial(m.id)} disabled={deletingIds.has(m.id)}>
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
        {drafts.map(d => (
          <Grid item xs={6} sm={4} md={3} key={d.id}>
            <Card variant="outlined" sx={{ position: 'relative', opacity: d.status === 'error' ? 0.7 : 1 }}>
              <CardContent>
                <Typography variant="subtitle2" noWrap>{d.file.name}</Typography>
                {d.status === 'error' && <Typography variant="caption" color="error">{d.error}</Typography>}
              </CardContent>
              {d.status === 'uploading' && <LinearProgress sx={{ position: 'absolute', bottom: 0, left: 0, right: 0 }} />}
              <CardActions sx={{ justifyContent: 'space-between' }}>
                {d.status === 'pending' && (
                  <Button size="small" onClick={() => startUpload(d.id)}>Upload</Button>
                )}
                {d.status === 'error' && (
                  <Button size="small" onClick={() => startUpload(d.id)}>Retry</Button>
                )}
                <Button size="small" color="inherit" onClick={() => setDrafts(ds => ds.filter(x => x.id !== d.id))}>Remove</Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
      {!materialsLoading && materials.length === 0 && drafts.length === 0 && (
        <Typography variant="body2" sx={{ mt: 3 }}>No materials yet. Use &quot;Add Files&quot; to upload.</Typography>
      )}
    </Box>
  );
};
