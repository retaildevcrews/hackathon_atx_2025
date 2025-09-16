import React, { useState, useCallback } from 'react';
import { Box, TextField, Button, Stack, Typography, FormControl, InputLabel, Select, MenuItem } from '@mui/material';

export interface DecisionKitFormValues { name: string; description: string; rubricId: string; }
export interface DecisionKitFormProps {
  initial?: Partial<DecisionKitFormValues>;
  loading?: boolean;
  error?: string | null;
  rubrics?: { id: string; name: string }[];
  rubricsLoading?: boolean;
  onSubmit: (values: { name: string; description?: string; rubricId: string }) => Promise<any> | any;
  onCancel?: () => void;
  submitLabel?: string;
}

const NAME_MAX = 100;
const DESC_MAX = 1000;

export const DecisionKitForm: React.FC<DecisionKitFormProps> = ({ initial, loading, error, rubrics, rubricsLoading, onSubmit, onCancel, submitLabel = 'Create' }) => {
  const [name, setName] = useState(initial?.name || '');
  const [description, setDescription] = useState(initial?.description || '');
  const [rubricId, setRubricId] = useState(initial?.rubricId || '');
  const [touched, setTouched] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const effectiveLoading = loading || submitting;

  const nameError = touched && (!name.trim() ? 'Name is required' : (name.trim().length > NAME_MAX ? `Name max length ${NAME_MAX}` : undefined));
  const rubricError = touched && !rubricId ? 'Rubric is required' : undefined;
  const descError = description && description.length > DESC_MAX ? `Description max length ${DESC_MAX}` : undefined;

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (nameError || descError || rubricError || !name.trim()) return;
    try {
      setSubmitting(true);
      await onSubmit({ name: name.trim(), description: description.trim() || undefined, rubricId });
    } finally { setSubmitting(false); }
  }, [name, description, rubricId, onSubmit, nameError, descError, rubricError]);

  return (
    <Box component="form" onSubmit={handleSubmit} noValidate>
      <Stack spacing={2}>
        {error && <Typography color="error" role="alert">{error}</Typography>}
        <TextField
          label="Name"
          value={name}
          onChange={e => setName(e.target.value)}
          onBlur={() => setTouched(true)}
          required
          disabled={effectiveLoading}
          error={!!nameError}
          helperText={nameError ? nameError : `${name.trim().length}/${NAME_MAX}`}
          inputProps={{ maxLength: NAME_MAX + 10 }}
        />
  <FormControl fullWidth required disabled={effectiveLoading || !!(!rubrics || rubricsLoading)} error={!!rubricError}>
          <InputLabel id="rubric-select-label">Rubric</InputLabel>
          <Select
            labelId="rubric-select-label"
            label="Rubric"
            value={rubricId}
            onChange={e => setRubricId(e.target.value)}
            onBlur={() => setTouched(true)}
          >
            {rubrics?.map((r: { id: string; name: string }) => <MenuItem key={r.id} value={r.id}>{r.name}</MenuItem>)}
          </Select>
          <Typography variant="caption" color={rubricError ? 'error' : 'text.secondary'} sx={{ mt: 0.5 }}>
            {rubricError || (rubricsLoading ? 'Loading rubrics...' : 'Select the rubric snapshot for this kit')}
          </Typography>
        </FormControl>
        <TextField
          label="Description"
            value={description}
          onChange={e => setDescription(e.target.value)}
          multiline rows={4}
          disabled={effectiveLoading}
          error={!!descError}
          helperText={descError ? descError : `${description.length}/${DESC_MAX}`}
          inputProps={{ maxLength: DESC_MAX + 50 }}
        />
        <Stack direction="row" spacing={2}>
          {onCancel && <Button type="button" variant="text" disabled={effectiveLoading} onClick={onCancel}>Cancel</Button>}
          <Button type="submit" variant="contained" disabled={effectiveLoading || !!nameError || !!descError || !!rubricError}>{submitLabel}</Button>
        </Stack>
      </Stack>
    </Box>
  );
};
