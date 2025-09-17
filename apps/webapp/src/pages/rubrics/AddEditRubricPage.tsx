import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  Paper,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Breadcrumbs,
  Link,
  CircularProgress,
  Alert,
  Snackbar
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import { Link as RouterLink, useParams, useNavigate } from 'react-router-dom';
import { createRubric, updateRubric, fetchRubricDetail, fetchAvailableCriteria } from '../../api/rubrics';
import { Rubric } from '../../types/rubric';
import { CriteriaRecord } from '../../api/criteria';

export const AddEditRubricPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditMode = Boolean(id);

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [selectedCriteriaIds, setSelectedCriteriaIds] = useState<string[]>([]);

  // Data state
  const [availableCriteria, setAvailableCriteria] = useState<CriteriaRecord[]>([]);
  const [originalRubric, setOriginalRubric] = useState<Rubric | null>(null);

  // UI state
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [snackbar, setSnackbar] = useState<{open: boolean; message: string; severity: 'success' | 'error'}>({
    open: false,
    message: '',
    severity: 'success'
  });

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load available criteria
      const criteria = await fetchAvailableCriteria();
      setAvailableCriteria(criteria);

      // If editing, load the rubric details
      if (isEditMode && id) {
        const rubric = await fetchRubricDetail(id);
        setOriginalRubric(rubric);
        setName(rubric.name);
        setDescription(rubric.description);
        setSelectedCriteriaIds(rubric.criteria.map(c => c.id));
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!name.trim()) {
      errors.name = 'Name is required';
    }

    if (!description.trim()) {
      errors.description = 'Description is required';
    }

    if (selectedCriteriaIds.length === 0) {
      errors.criteria = 'Please select at least one criterion';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setSaving(true);
    setError(null);

    try {
      const selectedCriteria = availableCriteria
        .filter(criterion => selectedCriteriaIds.includes(criterion.id))
        .map(criterion => ({
          id: criterion.id,
          name: criterion.name,
          description: criterion.description || '',
          definition: criterion.definition || ''
        }));

      const rubricData = {
        name: name.trim(),
        description: description.trim(),
        criteria: selectedCriteria
      };

      if (isEditMode && id) {
        await updateRubric(id, rubricData);
        setSnackbar({
          open: true,
          message: 'Rubric updated successfully',
          severity: 'success'
        });
        // Navigate back to detail page after short delay
        setTimeout(() => navigate(`/rubrics/${id}`), 1000);
      } else {
        const newRubric = await createRubric(rubricData);
        setSnackbar({
          open: true,
          message: 'Rubric created successfully',
          severity: 'success'
        });
        // Navigate to new rubric detail page after short delay
        setTimeout(() => navigate(`/rubrics/${newRubric.id}`), 1000);
      }
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: err.message || 'Failed to save rubric',
        severity: 'error'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCriteriaChange = (criterionId: string) => {
    setSelectedCriteriaIds(prev =>
      prev.includes(criterionId)
        ? prev.filter(id => id !== criterionId)
        : [...prev, criterionId]
    );

    // Clear criteria error if user selects at least one
    if (formErrors.criteria && selectedCriteriaIds.length >= 0) {
      setFormErrors(prev => ({ ...prev, criteria: '' }));
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const pageTitle = isEditMode ? 'Edit Rubric' : 'Create Rubric';
  const backPath = isEditMode ? `/rubrics/${id}` : '/rubrics';

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button onClick={loadData} variant="contained" sx={{ mr: 2 }}>
          Retry
        </Button>
        <Button component={RouterLink} to="/rubrics" variant="outlined" startIcon={<ArrowBackIcon />}>
          Back to Rubrics
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link component={RouterLink} to="/rubrics" color="inherit">
          Rubrics
        </Link>
        {isEditMode && originalRubric && (
          <Link component={RouterLink} to={`/rubrics/${id}`} color="inherit">
            {originalRubric.name}
          </Link>
        )}
        <Typography color="text.primary">{pageTitle}</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          {pageTitle}
        </Typography>
        <Button
          component={RouterLink}
          to={backPath}
          variant="outlined"
          startIcon={<ArrowBackIcon />}
        >
          Cancel
        </Button>
      </Box>

      {/* Form */}
      <Paper sx={{ p: 4 }}>
        <form onSubmit={handleSubmit}>
          <Box sx={{ maxWidth: 800 }}>
            {/* Name Field */}
            <TextField
              label="Name"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (formErrors.name && e.target.value.trim()) {
                  setFormErrors(prev => ({ ...prev, name: '' }));
                }
              }}
              required
              fullWidth
              margin="normal"
              error={!!formErrors.name}
              helperText={formErrors.name}
            />

            {/* Description Field */}
            <TextField
              label="Description"
              value={description}
              onChange={(e) => {
                setDescription(e.target.value);
                if (formErrors.description && e.target.value.trim()) {
                  setFormErrors(prev => ({ ...prev, description: '' }));
                }
              }}
              required
              fullWidth
              margin="normal"
              multiline
              minRows={3}
              maxRows={6}
              error={!!formErrors.description}
              helperText={formErrors.description || 'Provide a clear description of what this rubric evaluates'}
            />

            {/* Criteria Selection */}
            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" gutterBottom>
                Criteria Selection
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Select the criteria that will be included in this rubric. Each criterion will be used to evaluate submissions.
              </Typography>

              {formErrors.criteria && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {formErrors.criteria}
                </Alert>
              )}

              {availableCriteria.length === 0 ? (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  No criteria available. You need to create criteria before creating rubrics.
                </Alert>
              ) : (
                <FormGroup>
                  {availableCriteria.map((criterion) => (
                    <FormControlLabel
                      key={criterion.id}
                      control={
                        <Checkbox
                          checked={selectedCriteriaIds.includes(criterion.id)}
                          onChange={() => handleCriteriaChange(criterion.id)}
                        />
                      }
                      label={
                        <Box sx={{ ml: 1 }}>
                          <Typography variant="subtitle1" component="div">
                            {criterion.name}
                          </Typography>
                          {criterion.description && (
                            <Typography variant="body2" color="text.secondary">
                              {criterion.description}
                            </Typography>
                          )}
                        </Box>
                      }
                      sx={{
                        alignItems: 'flex-start',
                        mb: 2,
                        '& .MuiCheckbox-root': {
                          pt: 0
                        }
                      }}
                    />
                  ))}
                </FormGroup>
              )}
            </Box>

            {/* Submit Button */}
            <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={saving || availableCriteria.length === 0}
                startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
                sx={{ minWidth: 150 }}
              >
                {saving ? 'Saving...' : (isEditMode ? 'Update Rubric' : 'Create Rubric')}
              </Button>
              <Button
                component={RouterLink}
                to={backPath}
                variant="outlined"
                size="large"
                disabled={saving}
              >
                Cancel
              </Button>
            </Box>
          </Box>
        </form>
      </Paper>

      {/* Success/Error Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};
