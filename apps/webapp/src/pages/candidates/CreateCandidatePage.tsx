import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Box, Button, TextField, Typography, Alert, Stack } from '@mui/material';
import { useCreateCandidate } from '../../hooks/useCreateCandidate';

export const CreateCandidatePage: React.FC = () => {
  const { kitId } = useParams();
  const navigate = useNavigate();
  const { create, creating, error } = useCreateCandidate();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [touched, setTouched] = useState(false);

  const nameError = touched && !name.trim() ? 'Name is required' : undefined;

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setTouched(true);
    if (nameError || !kitId) return;
    const candidate = await create({ name, description, decisionKitId: kitId });
    if (candidate) {
      navigate(`/candidates/${candidate.id}/edit`);
    }
  }

  return (
    <Box maxWidth="md" mx="auto">
      <Typography variant="h4" gutterBottom>New Candidate</Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Box component="form" onSubmit={onSubmit} noValidate>
        <Stack spacing={2}>
          <TextField
            label="Name"
            value={name}
            onChange={e => setName(e.target.value)}
            onBlur={() => setTouched(true)}
            error={!!nameError}
            helperText={nameError || ' '} required fullWidth
            inputProps={{ maxLength: 120 }}
          />
          <TextField
            label="Description"
            value={description}
            onChange={e => setDescription(e.target.value)}
            multiline minRows={3} fullWidth inputProps={{ maxLength: 2000 }}
          />
          <Stack direction="row" spacing={2}>
            <Button type="submit" variant="contained" disabled={creating || !!nameError || !kitId}>{creating ? 'Creating...' : 'Create & Continue'}</Button>
            <Button variant="outlined" onClick={() => navigate(`/decision-kits/${kitId}`)}>Cancel</Button>
          </Stack>
        </Stack>
      </Box>
    </Box>
  );
};
