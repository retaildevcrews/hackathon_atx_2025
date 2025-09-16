
import React, { useState, useEffect } from 'react';
import { Rubric } from '../types/rubric';
import { useCriteria } from '../hooks/useCriteria';
import { Box, Typography, TextField, Checkbox, Button, FormGroup, FormControlLabel, FormControl, FormHelperText } from '@mui/material';

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
  const [submitted, setSubmitted] = useState(false);
  const [touchedName, setTouchedName] = useState(false);
  const [touchedDescription, setTouchedDescription] = useState(false);
  const [touchedCriteria, setTouchedCriteria] = useState(false);

  useEffect(() => {
    refresh();
  }, [refresh]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitted(true);
    const hasName = name.trim().length > 0;
    const hasDescription = description.trim().length > 0;
    const hasCriteria = selectedCriteria.length > 0;
    if (!hasName || !hasDescription || !hasCriteria) return;
    const selected = criteria.filter(c => c.id && selectedCriteria.includes(String(c.id))).map(c => ({
      ...c,
      id: String(c.id)
    }));
    onSave({ name, description, criteria: selected });
  }

  function handleCriteriaChange(id: string | undefined) {
    if (!id) return;
    if (!touchedCriteria) setTouchedCriteria(true);
    setSelectedCriteria(prev =>
      prev.includes(String(id)) ? prev.filter(cid => cid !== String(id)) : [...prev, String(id)]
    );
  }

  // Validation helpers
  const nameErrorText = !name.trim() ? 'Name is required.' : '';
  const descriptionErrorText = !description.trim() ? 'Description is required.' : '';
  const criteriaErrorText = selectedCriteria.length === 0 ? 'Please select at least one criterion.' : '';
  const showNameError = (submitted || touchedName) && !!nameErrorText;
  const showDescriptionError = (submitted || touchedDescription) && !!descriptionErrorText;
  const showCriteriaError = (submitted || touchedCriteria) && !!criteriaErrorText;
  const formInvalid = !!nameErrorText || !!descriptionErrorText || !!criteriaErrorText;

  return (
    <form onSubmit={handleSubmit}>
      <Box sx={{ maxWidth: 500, mx: 'auto', mt: 2, p: 2, borderRadius: 2, boxShadow: 2, bgcolor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>{initialRubric ? 'Edit Rubric' : 'Create Rubric'}</Typography>
        <TextField
          label="Name"
          value={name}
          onChange={e => setName(e.target.value)}
          onBlur={() => setTouchedName(true)}
          required
          fullWidth
          margin="normal"
          error={showNameError}
          helperText={showNameError ? nameErrorText : ' '}
        />
        <TextField
          label="Description"
          value={description}
          onChange={e => setDescription(e.target.value)}
          onBlur={() => setTouchedDescription(true)}
          required
          fullWidth
          margin="normal"
          multiline
          minRows={2}
          error={showDescriptionError}
          helperText={showDescriptionError ? descriptionErrorText : ' '}
        />
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle1" gutterBottom>Criteria</Typography>
          <FormControl error={showCriteriaError} component="fieldset" variant="standard">
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
            <FormHelperText>{showCriteriaError ? criteriaErrorText : ' '}</FormHelperText>
          </FormControl>
        </Box>
        <Button
          type="submit"
          variant="contained"
          color="primary"
          disabled={loading || formInvalid}
          sx={{ mt: 3 }}
          fullWidth
        >
          {loading ? 'Saving...' : 'Save Rubric'}
        </Button>
      </Box>
    </form>
  );
};
