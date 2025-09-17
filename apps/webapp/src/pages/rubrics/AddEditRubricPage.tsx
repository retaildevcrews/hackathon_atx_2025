import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Breadcrumbs, Link, CircularProgress, Alert, Snackbar } from '@mui/material';
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import { Link as RouterLink, useParams, useNavigate, useLocation } from 'react-router-dom';
import { createRubric, updateRubric, fetchRubricDetail } from '../../api/rubrics';
import { Rubric } from '../../types/rubric';
import { RubricForm } from '../../components/RubricForm';

export const AddEditRubricPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const fromPath = (location.state as any)?.from as string | undefined;
  const isEditMode = Boolean(id);

  // Data state
  const [originalRubric, setOriginalRubric] = useState<Rubric | null>(null);

  // UI state
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
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
      if (isEditMode && id) {
        const rubric = await fetchRubricDetail(id);
        setOriginalRubric(rubric);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (rubricData: Omit<Rubric, 'id'>) => {
    setSaving(true);
    setError(null);
    try {
      if (isEditMode && id) {
        await updateRubric(id, rubricData);
        setSnackbar({ open: true, message: 'Rubric updated successfully', severity: 'success' });
        setTimeout(() => navigate(fromPath || `/rubrics/${id}`), 1000);
      } else {
        const newRubric = await createRubric(rubricData);
        setSnackbar({ open: true, message: 'Rubric created successfully', severity: 'success' });
        setTimeout(() => navigate(fromPath || `/rubrics/${newRubric.id}`), 1000);
      }
    } catch (err: any) {
      setSnackbar({ open: true, message: err.message || 'Failed to save rubric', severity: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const pageTitle = isEditMode ? 'Edit Rubric' : 'Create Rubric';
  const backPath = fromPath || (isEditMode ? `/rubrics/${id}` : '/rubrics');

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
      <RubricForm
        initialRubric={originalRubric ?? undefined}
        onSave={handleSave}
        loading={saving || loading}
        onCancel={() => navigate(backPath)}
      />

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
