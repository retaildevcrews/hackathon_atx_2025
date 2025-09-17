import React, { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Checkbox, FormControlLabel, Typography, Alert, CircularProgress, Box } from '@mui/material';

export interface DeleteDecisionKitDialogProps {
  open: boolean;
  kitName?: string;
  loading?: boolean;
  error?: string | null;
  onClose: () => void;
  onConfirm: () => Promise<any> | any;
}

export const DeleteDecisionKitDialog: React.FC<DeleteDecisionKitDialogProps> = ({ open, kitName, loading, error, onClose, onConfirm }) => {
  const [confirmed, setConfirmed] = useState(false);

  useEffect(() => { if (!open) setConfirmed(false); }, [open]);

  return (
    <Dialog open={open} onClose={() => !loading && onClose()} aria-labelledby="delete-dk-title" fullWidth maxWidth="sm">
      <DialogTitle id="delete-dk-title">Delete Decision Kit</DialogTitle>
      <DialogContent dividers>
        <Typography gutterBottom>
          This will permanently delete the decision kit{kitName ? ` "${kitName}"` : ''} and all associated data:
        </Typography>
        <ul>
          <li>Rubric associations & weights</li>
          <li>Candidates & candidate materials</li>
          <li>Assessments / reports</li>
        </ul>
        <Typography variant="body2" color="error" gutterBottom>
          This action cannot be undone.
        </Typography>
        {error && <Alert severity="error" sx={{ mt: 1 }}>{error}</Alert>}
        <FormControlLabel control={<Checkbox disabled={loading} checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />} label="I understand this will permanently remove all associated data." />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>Cancel</Button>
        <Button onClick={onConfirm} disabled={!confirmed || loading} color="error" variant="contained" startIcon={loading ? <Box component="span" sx={{ display: 'flex' }}><CircularProgress size={16} /></Box> : undefined}>
          Delete
        </Button>
      </DialogActions>
    </Dialog>
  );
};
