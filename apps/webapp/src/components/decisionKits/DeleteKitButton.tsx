import React, { useState, useCallback } from 'react';
import { Button, Snackbar, Alert } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { useNavigate } from 'react-router-dom';
import { useDeleteDecisionKit } from '../../hooks/useDeleteDecisionKit';
import { DeleteDecisionKitDialog } from './DeleteDecisionKitDialog';

export interface DeleteKitButtonProps {
  kitId: string;
  kitName?: string;
  getList?: () => any;
  setList?: (next: any) => void;
}

export const DeleteKitButton: React.FC<DeleteKitButtonProps> = ({ kitId, kitName, getList, setList }) => {
  const [open, setOpen] = useState(false);
  const [toast, setToast] = useState<{ open: boolean; message: string; severity: 'success' | 'warning' } | null>(null);
  const navigate = useNavigate();
  const { deleteDecisionKit, loading, error } = useDeleteDecisionKit({
    getList,
    setList,
    onSuccess: () => {
      navigate('/');
      setOpen(false);
      setToast({ open: true, message: 'Decision kit deleted', severity: 'success' });
    },
    onError: (e) => {
      if (e?.response?.status === 404) {
        navigate('/');
        setToast({ open: true, message: 'Decision kit already removed', severity: 'warning' });
      }
    }
  });

  const handleConfirm = useCallback(async () => {
    await deleteDecisionKit(kitId);
  }, [deleteDecisionKit, kitId]);

  return (
    <>
  <Button color="error" variant="outlined" onClick={() => setOpen(true)} size="small" startIcon={<DeleteIcon />}>Delete</Button>
      <DeleteDecisionKitDialog
        open={open}
        kitName={kitName}
        loading={loading}
        error={error}
        onClose={() => setOpen(false)}
        onConfirm={handleConfirm}
      />
      <Snackbar
        open={!!toast?.open}
        autoHideDuration={4000}
        onClose={() => setToast(t => t ? { ...t, open: false } : t)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        message={undefined}
      >
        {toast ? <Alert severity={toast.severity} variant="filled" sx={{ width: '100%' }}>{toast.message}</Alert> : <></>}
      </Snackbar>
    </>
  );
};
