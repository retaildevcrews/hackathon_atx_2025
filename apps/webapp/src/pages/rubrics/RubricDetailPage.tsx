import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Card,
  CardContent,
  List,
  ListItem,
  Divider,
  Breadcrumbs,
  Link,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Snackbar,
  Chip
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material';
import { Link as RouterLink, useParams, useNavigate } from 'react-router-dom';
import { fetchRubricDetail, deleteRubric } from '../../api/rubrics';
import { Rubric } from '../../types/rubric';

export const RubricDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [rubric, setRubric] = useState<Rubric | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [snackbar, setSnackbar] = useState<{open: boolean; message: string; severity: 'success' | 'error'}>({
    open: false,
    message: '',
    severity: 'success'
  });

  useEffect(() => {
    loadRubric();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const loadRubric = async () => {
    if (!id) {
      setError('Invalid rubric ID');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const rubricData = await fetchRubricDetail(id);
      setRubric(rubricData);
    } catch (err: any) {
      setError(err.message || 'Failed to load rubric details');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!rubric) return;

    setDeleteLoading(true);
    try {
      await deleteRubric(rubric.id);
      setSnackbar({
        open: true,
        message: `Rubric "${rubric.name}" deleted successfully`,
        severity: 'success'
      });
      // Navigate back to list after short delay to show success message
      setTimeout(() => navigate('/rubrics'), 1000);
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to delete rubric. It may be associated with decision kits.',
        severity: 'error'
      });
    } finally {
      setDeleteLoading(false);
      setDeleteDialogOpen(false);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
  };

  const handleSnackbarClose = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

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
        <Button onClick={loadRubric} variant="contained" sx={{ mr: 2 }}>
          Retry
        </Button>
        <Button component={RouterLink} to="/rubrics" variant="outlined" startIcon={<ArrowBackIcon />}>
          Back to Rubrics
        </Button>
      </Box>
    );
  }

  if (!rubric) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 2 }}>
          Rubric not found
        </Alert>
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
        <Typography color="text.primary">{rubric.name}</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            {rubric.name}
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            {rubric.description}
          </Typography>
          <Chip
            label={`${rubric.criteria.length} criteria`}
            color="primary"
            variant="outlined"
          />
        </Box>
        <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
          <Button
            component={RouterLink}
            to={`/rubrics/${rubric.id}/edit`}
            variant="contained"
            startIcon={<EditIcon />}
          >
            Edit
          </Button>
          <Button
            onClick={handleDeleteClick}
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
          >
            Delete
          </Button>
        </Box>
      </Box>

      {/* Criteria Section */}
      <Paper sx={{ mt: 3 }}>
        <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h5" component="h2">
            Criteria
          </Typography>
          <Typography variant="body2" color="text.secondary">
            The following criteria are included in this rubric:
          </Typography>
        </Box>
        {rubric.criteria.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary">
              No criteria defined
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Edit this rubric to add criteria.
            </Typography>
          </Box>
        ) : (
          <List sx={{ py: 0 }}>
            {rubric.criteria.map((criterion, index) => (
              <React.Fragment key={criterion.id}>
                <ListItem sx={{ py: 3 }}>
                  <Card sx={{ width: '100%', boxShadow: 1 }}>
                    <CardContent>
                      <Typography variant="h6" component="h3" gutterBottom>
                        {criterion.name}
                      </Typography>
                      {criterion.description && (
                        <Typography variant="body1" color="text.secondary" paragraph>
                          {criterion.description}
                        </Typography>
                      )}
                      {criterion.definition && (
                        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1, border: 1, borderColor: 'grey.200' }}>
                          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
                            Definition:
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {criterion.definition}
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </ListItem>
                {index < rubric.criteria.length - 1 && <Divider component="li" />}
              </React.Fragment>
            ))}
          </List>
        )}
      </Paper>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          Delete Rubric
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Are you sure you want to delete the rubric &ldquo;{rubric.name}&rdquo;?
            This action cannot be undone and will remove all {rubric.criteria.length} criteria
            associated with this rubric. If this rubric is used in decision kits,
            the deletion may fail.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} disabled={deleteLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleteLoading}
            startIcon={deleteLoading ? <CircularProgress size={20} /> : <DeleteIcon />}
          >
            {deleteLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

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
