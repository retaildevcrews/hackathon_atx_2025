import React, { useState } from 'react';
import {
  Paper, Table, TableHead, TableBody, TableRow, TableCell,
  IconButton, Collapse, Box, Typography, CircularProgress,
  Stack, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Snackbar, Alert
} from '@mui/material';
import { KeyboardArrowDown, KeyboardArrowUp, Add, Refresh, Delete } from '@mui/icons-material';
import { useCriteria } from '../hooks/useCriteria';

export const CriteriaTable: React.FC = () => {
  const { criteria, loading, error, refresh, create, remove, apiBase } = useCriteria();
  const [openRows, setOpenRows] = useState<Record<string, boolean>>({});
  const [dialogOpen, setDialogOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [definition, setDefinition] = useState('');
  const [snack, setSnack] = useState<{open: boolean; msg: string; severity: 'success' | 'error'}>({open:false,msg:'',severity:'success'});

  const toggle = (id: string) => setOpenRows(prev => ({ ...prev, [id]: !prev[id] }));

  const handleCreate = async () => {
    try {
      await create({ name, description, definition });
      setSnack({ open: true, msg: 'Created criteria', severity: 'success' });
      setName(''); setDescription(''); setDefinition('');
      setDialogOpen(false);
    } catch (e: any) {
      setSnack({ open: true, msg: e.message || 'Create failed', severity: 'error' });
    }
  };

  const handleDelete = async (id?: string) => {
    if (!id) return;
    if (!confirm('Delete this criteria?')) return;
    try {
      await remove(id);
      setSnack({ open: true, msg: 'Deleted', severity: 'success' });
    } catch (e: any) {
      setSnack({ open: true, msg: e.message || 'Delete failed', severity: 'error' });
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Criteria</Typography>
        <Stack direction="row" spacing={1}>
          <Button variant="outlined" startIcon={<Refresh />} onClick={refresh} disabled={loading}>Refresh</Button>
          <Button variant="contained" startIcon={<Add />} onClick={() => setDialogOpen(true)}>New</Button>
        </Stack>
      </Stack>

      {loading && <Stack alignItems="center" py={4}><CircularProgress /></Stack>}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} action={<Button color="inherit" size="small" onClick={refresh}>Retry</Button>}>
          {error} (API: {apiBase})
        </Alert>
      )}
      {!loading && criteria.length === 0 && <Typography>No criteria defined yet.</Typography>}

      {!loading && criteria.length > 0 && (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell />
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell width="120px">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {criteria.map(c => {
              const isOpen = !!openRows[c.id!];
              return (
                <React.Fragment key={c.id}>
                  <TableRow hover>
                    <TableCell padding="checkbox">
                      <IconButton size="small" onClick={() => toggle(c.id!)} aria-label={isOpen ? 'collapse' : 'expand'}>
                        {isOpen ? <KeyboardArrowUp /> : <KeyboardArrowDown />}
                      </IconButton>
                    </TableCell>
                    <TableCell>{c.name}</TableCell>
                    <TableCell>{c.description}</TableCell>
                    <TableCell>
                      <IconButton color="error" size="small" onClick={() => handleDelete(c.id)}>
                        <Delete fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={4}>
                      <Collapse in={isOpen} timeout="auto" unmountOnExit>
                        <Box margin={2}>
                          <Typography variant="subtitle2" gutterBottom>Definition</Typography>
                          <Box component="pre" sx={{ whiteSpace: 'pre-wrap', fontSize: 12, bgcolor: 'grey.100', p:1, borderRadius:1 }}>
                            {c.definition}
                          </Box>
                        </Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              );
            })}
          </TableBody>
        </Table>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Criteria</DialogTitle>
        <DialogContent sx={{ pt: 1 }}>
          <Stack spacing={2} mt={1}>
            <TextField label="Name" fullWidth value={name} onChange={e => setName(e.target.value)} required />
            <TextField label="Description" fullWidth value={description} onChange={e => setDescription(e.target.value)} required />
            <TextField label="Definition" fullWidth multiline minRows={5} value={definition} onChange={e => setDefinition(e.target.value)} required placeholder="JSON or markdown" />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate} disabled={!name || !description || !definition}>Create</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snack.open} autoHideDuration={3000} onClose={() => setSnack(s => ({...s, open:false}))}>
        <Alert severity={snack.severity} onClose={() => setSnack(s => ({...s, open:false}))}>{snack.msg}</Alert>
      </Snackbar>
    </Paper>
  );
};
