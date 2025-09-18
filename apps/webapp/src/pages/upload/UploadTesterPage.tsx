import React, { useState, useCallback } from 'react';
import { Box, Button, TextField, Typography, Alert, Paper, Stack, Divider, LinearProgress } from '@mui/material';

interface UploadResult {
  blobPath: string;
  sha256: string;
  size: number;
}

export const UploadTesterPage: React.FC = () => {
  const [endpoint, setEndpoint] = useState<string>(import.meta.env.VITE_UPLOAD_ENDPOINT || '');
  const [secret, setSecret] = useState<string>('');
  const [contextType, setContextType] = useState('candidate');
  const [contextId, setContextId] = useState('demo');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadResult | null>(null);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    if (!endpoint) {
      setError('Endpoint required');
      return;
    }
    if (!file) {
      setError('Select a file');
      return;
    }
    const form = new FormData();
    form.append('contextType', contextType);
    form.append('contextId', contextId);
    form.append('file', file);
    setLoading(true);
    try {
      const res = await fetch(endpoint.replace(/\/$/, '') + '/api/upload', {
        method: 'POST',
        body: form,
        headers: secret ? { 'X-Internal-Upload-Key': secret } : undefined,
      });
      if (!res.ok) {
        const text = await res.text();
        setError(`Upload failed (${res.status}): ${text}`);
      } else {
        const json = await res.json();
        setResult(json as UploadResult);
      }
    } catch (err: any) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  }, [endpoint, file, contextType, contextId, secret]);

  return (
    <Box p={3} maxWidth={800} mx="auto">
      <Typography variant="h4" gutterBottom>Upload Tester</Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Standalone tool to exercise the Generic Upload Function. Provide an endpoint (e.g. http://localhost:7071), optional shared secret (omit if bypass mode enabled on server), and select a file.
      </Typography>
      <Paper variant="outlined" sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            <TextField label="Endpoint" value={endpoint} onChange={e => setEndpoint(e.target.value)} fullWidth required placeholder="http://localhost:7071" />
            <TextField label="Shared Secret (raw)" value={secret} onChange={e => setSecret(e.target.value)} fullWidth type="password" autoComplete="off" />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField label="Context Type" value={contextType} onChange={e => setContextType(e.target.value)} required fullWidth />
              <TextField label="Context ID" value={contextId} onChange={e => setContextId(e.target.value)} required fullWidth />
            </Stack>
            <Button variant="outlined" component="label">
              {file ? `Selected: ${file.name}` : 'Choose File'}
              <input hidden type="file" onChange={onFileChange} />
            </Button>
            {loading && <LinearProgress />}
            <Stack direction="row" spacing={2}>
              <Button type="submit" variant="contained" disabled={loading || !file}>Upload</Button>
              <Button type="button" disabled={loading && !file} onClick={() => { setFile(null); setResult(null); setError(null); }}>Reset</Button>
            </Stack>
          </Stack>
        </form>
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {result && (
          <Alert severity="success" sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>Upload Success</Typography>
            <div><strong>Blob Path:</strong> {result.blobPath}</div>
            <div><strong>SHA256:</strong> {result.sha256}</div>
            <div><strong>Size:</strong> {result.size} bytes</div>
          </Alert>
        )}
        <Divider sx={{ my: 3 }} />
        <Typography variant="caption" color="text.secondary">
          Note: Maximum size enforced server-side (default 10MB). For demo auth bypass, server must set DISABLE_INTERNAL_UPLOAD_AUTH=true.
        </Typography>
      </Paper>
    </Box>
  );
};

export default UploadTesterPage;