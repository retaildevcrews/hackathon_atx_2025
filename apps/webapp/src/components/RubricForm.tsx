
import React, { useState, useEffect } from 'react';
import { Rubric, Criteria } from '../types/rubric';
import { useCriteria } from '../hooks/useCriteria';
import { Box, Typography, TextField, Checkbox, Button, FormGroup, FormControlLabel } from '@mui/material';

interface RubricFormProps {
  initialRubric?: Rubric;
  onSave: (rubric: Omit<Rubric, 'id'>) => void;
  loading?: boolean;
}

export const RubricForm: React.FC<RubricFormProps> = ({ initialRubric, onSave, loading }) => {
  const [name, setName] = useState(initialRubric?.name || '');
  const [description, setDescription] = useState(initialRubric?.description || '');
  const [selectedCriteria, setSelectedCriteria] = useState<string[]>(initialRubric?.criteria.map(c => c.id) || []);
  const { criteria, refresh } = useCriteria();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    refresh();
  }, [refresh]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!name.trim()) {
      setError('Name is required.');
      return;
    }
    if (!description.trim()) {
      setError('Description is required.');
      return;
    }
    if (selectedCriteria.length === 0) {
      setError('Please select at least one criterion.');
      return;
    }
    const selected = criteria.filter(c => c.id && selectedCriteria.includes(String(c.id))).map(c => ({
      ...c,
      id: String(c.id)
    }));
    onSave({ name, description, criteria: selected });
  }

  function handleCriteriaChange(id: string | undefined) {
    if (!id) return;
    setSelectedCriteria(prev =>
      prev.includes(String(id)) ? prev.filter(cid => cid !== String(id)) : [...prev, String(id)]
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <Box sx={{ maxWidth: 500, mx: 'auto', mt: 2, p: 2, borderRadius: 2, boxShadow: 2, bgcolor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>{initialRubric ? 'Edit Rubric' : 'Create Rubric'}</Typography>
        {error && (
          <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>
        )}
        <TextField
          label="Name"
          value={name}
          onChange={e => setName(e.target.value)}
          required
          fullWidth
          margin="normal"
        />
        <TextField
          label="Description"
          value={description}
          onChange={e => setDescription(e.target.value)}
          required
          fullWidth
          margin="normal"
          multiline
          minRows={2}
        />
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle1" gutterBottom>Criteria</Typography>
          <FormGroup>
            {criteria.map(c => (
              <FormControlLabel
                key={String(c.id)}
                control={
                  <Checkbox
                    checked={selectedCriteria.includes(String(c.id))}
                    onChange={() => handleCriteriaChange(c.id)}
                  />
                }
                label={c.name}
              />
            ))}
          </FormGroup>
        </Box>
        <Button
          type="submit"
          variant="contained"
          color="primary"
          disabled={loading}
          sx={{ mt: 3 }}
          fullWidth
        >
          {loading ? 'Saving...' : 'Save Rubric'}
        </Button>
      </Box>
    </form>
  );
};
