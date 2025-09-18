import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Box, Button, Paper, Stack, TextField, Typography } from '@mui/material';
import { assignRubricToDecisionKit } from '../../api/decisionKits';

export const DecisionKitAttachRubricPage: React.FC = () => {
  const { kitId } = useParams<{ kitId: string }>();
  const navigate = useNavigate();
  const [rubricId, setRubricId] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!kitId || !rubricId.trim()) return;
    setSubmitting(true);
    try {
      await assignRubricToDecisionKit(kitId, rubricId.trim());
      navigate(`/decision-kits/${kitId}`);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 600, mx: 'auto', mt: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Stack spacing={2}>
          <Typography variant="h6">Attach a Rubric to Decision Kit</Typography>
          <TextField
            label="Rubric ID"
            value={rubricId}
            onChange={(e) => setRubricId(e.target.value)}
            required
          />
          <Button type="submit" variant="contained" disabled={submitting || !rubricId.trim()}>
            {submitting ? 'Attaching...' : 'Attach'}
          </Button>
          <Button type="button" variant="outlined" onClick={() => navigate(-1)}>Cancel</Button>
        </Stack>
      </Paper>
    </Box>
  );
};

export default DecisionKitAttachRubricPage;
