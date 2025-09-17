
import React, { useState, useEffect } from 'react';
import { Rubric } from '../types/rubric';
import type { Criteria as CriteriaModel } from '../hooks/useCriteria';
import { useCriteria } from '../hooks/useCriteria';
import { Box, Typography, TextField, Button, FormControl, FormHelperText, Paper, Stack, FormLabel, IconButton, Divider, Chip } from '@mui/material';
import { Add, Delete, Edit } from '@mui/icons-material';

interface RubricFormProps {
  initialRubric?: Rubric;
  onSave: (rubric: Omit<Rubric, 'id'>) => void;
  loading?: boolean;
}

export const RubricForm: React.FC<RubricFormProps> = ({ initialRubric, onSave, loading }) => {
  const [name, setName] = useState(initialRubric?.name || '');
  const [description, setDescription] = useState(initialRubric?.description || '');
  const { criteria, refresh, create, update } = useCriteria();
  const [entries, setEntries] = useState<Array<{ id?: string; name: string; description?: string; definition?: string; weight?: number }>>(
    initialRubric?.criteria?.map(c => ({ id: c.id, name: c.name, description: (c as any).description || '', definition: (c as any).definition || '', weight: (c as any).weight })) || []
  );
  const [newName, setNewName] = useState('');
  const [newWeight, setNewWeight] = useState<number | ''>('');
  const [addLoading, setAddLoading] = useState(false);
  const [errorText, setErrorText] = useState<string | null>(null);
  // const [editingId, setEditingId] = useState<string | null>(null);
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
    const hasCriteria = entries.length > 0;
    if (!hasName || !hasDescription || !hasCriteria) return;
    const normalized = entries.map(e => ({ id: e.id ?? '', name: e.name, description: e.description || '', definition: e.definition || '' }));
    onSave({ name, description, criteria: normalized });
  }

  async function handleAddEntry() {
    const nameToAdd = newName.trim();
    if (!nameToAdd) return;
    setErrorText(null);
    setAddLoading(true);
    try {
      // Reuse existing criterion by name if present (case-insensitive)
      const existing = criteria.find(
        (c: CriteriaModel) => c.name.trim().toLowerCase() === nameToAdd.toLowerCase()
      );
      const weightVal = newWeight === '' ? undefined : Number(newWeight);
      if (existing && existing.id) {
        setEntries((prev) => [...prev, { id: String(existing.id), name: existing.name, weight: weightVal }]);
      } else {
        // Persist new criterion; minimal fields
        const created = await (async () => {
          // useCriteria.create returns void; but backend returns created entity; update hook doesn't return.
          // Call API directly via create(), then take the last added from hook state; safer approach: call create and then refetch.
          await create({ name: nameToAdd, description: '', definition: '' } as any);
          // Find it again from updated hook state by name
          const found = criteria.find((c: CriteriaModel) => c.name.trim().toLowerCase() === nameToAdd.toLowerCase());
          return found ?? { id: undefined, name: nameToAdd };
        })();
        setEntries((prev) => [...prev, { id: created.id ? String(created.id) : undefined, name: created.name, weight: weightVal }]);
      }
      setNewName('');
      setNewWeight('');
      if (!touchedCriteria) setTouchedCriteria(true);
    } catch (e: any) {
      setErrorText('Failed to add criterion.');
    } finally {
      setAddLoading(false);
    }
  }

  function handleRemoveEntry(index: number) {
    setEntries(prev => prev.filter((_, i) => i !== index));
    if (!touchedCriteria) setTouchedCriteria(true);
  }

  // Future: open modal/editor for existing criteria
  function startEditEntry(id?: string) {
    if (!id) return;
    // setEditingId(id);
  }

  function updateEntry(index: number, patch: Partial<{ name: string; description?: string; definition?: string; weight?: number }>) {
    setEntries(prev => prev.map((e, i) => (i === index ? { ...e, ...patch } : e)));
  }

  async function persistIfNeeded(index: number) {
    const entry = entries[index];
    if (!entry?.id) return; // only persist for existing criteria
  const current = criteria.find((c: CriteriaModel) => String(c.id) === String(entry.id));
    if (!current) return;
    const newNameTrim = (entry.name || '').trim();
    const newDesc = (entry.description ?? '').trim();
    const newDef = (entry.definition ?? '').trim();
    const changed = (newNameTrim && newNameTrim !== current.name)
      || (newDesc !== (current as any).description)
      || (newDef !== (current as any).definition);
    if (!changed) return;
    try {
      setErrorText(null);
      await update(String(entry.id), {
        name: newNameTrim || current.name,
        description: newDesc,
        definition: newDef,
      } as any);
    } catch (e: any) {
      setErrorText('Failed to save criterion changes.');
    }
  }

  // Validation helpers
  const nameErrorText = !name.trim() ? 'Name is required.' : '';
  const descriptionErrorText = !description.trim() ? 'Description is required.' : '';
  const criteriaErrorText = entries.length === 0 ? 'Please add at least one criterion.' : '';
  const showNameError = (submitted || touchedName) && !!nameErrorText;
  const showDescriptionError = (submitted || touchedDescription) && !!descriptionErrorText;
  const showCriteriaError = (submitted || touchedCriteria) && !!criteriaErrorText;
  const formInvalid = !!nameErrorText || !!descriptionErrorText || !!criteriaErrorText;

  return (
    <form onSubmit={handleSubmit}>
      <Paper elevation={3} sx={{ maxWidth: 1200, width: '100%', mx: 'auto', mt: 2, p: 3 }}>
        <Stack spacing={2}>
          <Typography variant="h6">{initialRubric ? 'Edit Rubric' : 'Create Rubric'}</Typography>
          <TextField
            label="Name"
            value={name}
            onChange={e => setName(e.target.value)}
            onBlur={() => setTouchedName(true)}
            required
            fullWidth
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
            multiline
            minRows={2}
            error={showDescriptionError}
            helperText={showDescriptionError ? descriptionErrorText : ' '}
          />
          <Box>
            <FormControl error={showCriteriaError} component="fieldset" variant="standard" sx={{ width: '100%' }}>
              <FormLabel component="legend" sx={{ mb: 1 }}>Criteria</FormLabel>
              <Stack spacing={1} sx={{ mb: 1 }}>
                {entries.map((e, idx) => (
                  <Paper key={`${e.id ?? 'new'}-${idx}`} variant="outlined" sx={{ p: 1.5 }}>
                    <Stack spacing={1}>
                      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems={{ sm: 'center' }}>
                        <TextField
                          label="Name"
                          size="small"
                          value={e.name}
                          onChange={ev => updateEntry(idx, { name: ev.target.value })}
                          onBlur={() => persistIfNeeded(idx)}
                          sx={{ flex: 1 }}
                        />
                        <TextField
                          label="Weight"
                          type="number"
                          size="small"
                          value={e.weight ?? ''}
                          onChange={ev => updateEntry(idx, { weight: ev.target.value === '' ? undefined : Number(ev.target.value) })}
                          sx={{ width: 160 }}
                          inputProps={{ min: 0, step: 0.1 }}
                        />
                        {e.id && (
                          <IconButton aria-label="edit criterion" onClick={() => startEditEntry(e.id)}>
                            <Edit />
                          </IconButton>
                        )}
                        <IconButton aria-label="remove criterion" color="error" onClick={() => handleRemoveEntry(idx)}>
                          <Delete />
                        </IconButton>
                      </Stack>
                      <Box sx={{ width: '100%' }}>
                        <Box
                          sx={{
                            display: 'grid',
                            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
                            gap: 1
                          }}
                        >
                          <TextField
                            label="Description"
                            size="small"
                            value={e.description ?? ''}
                            onChange={ev => updateEntry(idx, { description: ev.target.value })}
                            onBlur={() => persistIfNeeded(idx)}
                            multiline
                            minRows={2}
                          />
                          <TextField
                            label="Definition"
                            size="small"
                            value={e.definition ?? ''}
                            onChange={ev => updateEntry(idx, { definition: ev.target.value })}
                            onBlur={() => persistIfNeeded(idx)}
                            multiline
                            minRows={2}
                          />
                        </Box>
                      </Box>
                    </Stack>
                  </Paper>
                ))}
              </Stack>
              <Divider sx={{ my: 1 }} />
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems={{ sm: 'center' }}>
                <TextField
                  label="Add new criterion"
                  size="small"
                  value={newName}
                  onChange={e => setNewName(e.target.value)}
                  sx={{ flex: 1 }}
                />
                <TextField
                  label="Weight"
                  type="number"
                  size="small"
                  value={newWeight}
                  onChange={e => setNewWeight(e.target.value === '' ? '' : Number(e.target.value))}
                  sx={{ width: 160 }}
                  inputProps={{ min: 0, step: 0.1 }}
                />
                <Button startIcon={<Add />} variant="outlined" onClick={handleAddEntry} disabled={addLoading}>
                  Add
                </Button>
              </Stack>
              <FormHelperText>{showCriteriaError ? criteriaErrorText : errorText ? errorText : ' '}</FormHelperText>
              {!!criteria.length && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">Available criteria:</Typography>
                  <Box sx={{ mt: 0.5, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {criteria.map((c: CriteriaModel) => (
                      <Chip
                        key={String(c.id)}
                        label={c.name}
                        onClick={() => setEntries(prev => [...prev, { id: String(c.id), name: c.name, description: (c as any).description || '', definition: (c as any).definition || '' }])}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </FormControl>
          </Box>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading || formInvalid}
            fullWidth
          >
            {loading ? 'Saving...' : 'Save Rubric'}
          </Button>
        </Stack>
      </Paper>
    </form>
  );
};
