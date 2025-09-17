import React, { useEffect, useState } from 'react';
import { Box, Button, TextField, Stack, Alert } from '@mui/material';

export interface CandidateFormValues {
  name: string;
  description: string;
}

export interface CandidateFormProps {
  mode: 'create' | 'edit';
  initial?: Partial<CandidateFormValues>;
  submitting: boolean;
  error?: string | null;
  onSubmit: (values: CandidateFormValues) => Promise<void> | void;
  onCancel: () => void;
}

export const CandidateForm: React.FC<CandidateFormProps> = ({
  mode,
  initial,
  submitting,
  error,
  onSubmit,
  onCancel,
}) => {
  const [name, setName] = useState(initial?.name || '');
  const [description, setDescription] = useState(initial?.description || '');
  const [touched, setTouched] = useState(false);

  useEffect(() => {
    setName(initial?.name || '');
    setDescription(initial?.description || '');
  }, [initial?.name, initial?.description]);

  const baseNameError = touched && !name.trim() ? 'Name is required' : undefined;
  const duplicateError = error && /(already exists)(.*decision kit)?/i.test(error) ? error : undefined;
  const nameError = baseNameError || duplicateError;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setTouched(true);
    if (nameError) return;
    await onSubmit({ name, description });
  }

  return (
    <Box component="form" noValidate onSubmit={handleSubmit}>
      <Stack spacing={2}>
        {error && !duplicateError && <Alert severity="error">{error}</Alert>}
        <TextField
          label="Name"
          value={name}
            onChange={e => setName(e.target.value)}
          onBlur={() => setTouched(true)}
          error={!!nameError}
          helperText={nameError || ' '}
          required fullWidth
          inputProps={{ maxLength: 120 }}
        />
        <TextField
          label="Description"
          value={description}
          onChange={e => setDescription(e.target.value)}
          multiline minRows={3} fullWidth inputProps={{ maxLength: 2000 }}
        />
        <Stack direction="row" spacing={2}>
          <Button type="submit" variant="contained" disabled={submitting || !!nameError}>
            {submitting ? (mode === 'create' ? 'Creating...' : 'Saving...') : (mode === 'create' ? 'Create & Continue' : 'Save Changes')}
          </Button>
          <Button variant="outlined" onClick={onCancel} disabled={submitting}>Cancel</Button>
        </Stack>
      </Stack>
    </Box>
  );
};
