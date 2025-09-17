import React, { useState } from 'react';
import { Box, Paper, Stack, TextField, Button, Typography, Alert, CircularProgress } from '@mui/material';
import { fetchRubricSummary } from '../api/rubrics';
import type { RubricSummary } from '../types/decisionKits';

interface AttachRubricFormProps {
  onAttach: (rubricId: string) => Promise<void> | void;
}

export const AttachRubricForm: React.FC<AttachRubricFormProps> = ({ onAttach }) => {
  const [rubricId, setRubricId] = useState('');
  const [preview, setPreview] = useState<RubricSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handlePreview() {
    setError(null);
    setPreview(null);
    if (!rubricId.trim()) {
      setError('Please enter a rubric id.');
      return;
    }
    try {
      setLoading(true);
      const data = await fetchRubricSummary(rubricId.trim());
      setPreview(data);
    } catch (e: any) {
      setError(e?.message || 'Failed to fetch rubric.');
    } finally {
      setLoading(false);
    }
  }

  async function handleAttach(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!rubricId.trim()) {
      setError('Please enter a rubric id.');
      return;
    }
    try {
      setLoading(true);
      await onAttach(rubricId.trim());
      setPreview(null);
    } catch (e: any) {
      setError(e?.message || 'Failed to attach rubric.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <form onSubmit={handleAttach}>
        <Stack spacing={2}>
          <Typography variant="subtitle1">Attach a Rubric</Typography>
          {error && <Alert severity="error">{error}</Alert>}
          <TextField
            label="Rubric ID"
            value={rubricId}
            onChange={e => setRubricId(e.target.value)}
            placeholder="Enter rubric id (UUID)"
            fullWidth
          />
          <Box display="flex" gap={1}>
            <Button variant="outlined" onClick={handlePreview} disabled={loading}>Preview</Button>
            <Button type="submit" variant="contained" disabled={loading || !rubricId.trim()}>
              {loading ? <CircularProgress size={20} /> : 'Attach'}
            </Button>
          </Box>
          {preview && (
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>{preview.name}</Typography>
              {preview.description && <Typography variant="body2" color="text.secondary">{preview.description}</Typography>}
              <Typography variant="caption" color="text.secondary">Criteria: {preview.criteria.length}</Typography>
            </Box>
          )}
        </Stack>
      </form>
    </Paper>
  );
};
