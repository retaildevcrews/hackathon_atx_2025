import { useState } from 'react';
import { uploadCandidateMaterial, deleteCandidateMaterial } from '../api/candidates';
import { CandidateMaterial } from '../types/candidates';

export function useUploadCandidateMaterial(candidateId: string | null) {
  const [uploadingIds, setUploadingIds] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);

  async function upload(file: File, signal?: AbortSignal): Promise<CandidateMaterial | null> {
    if (!candidateId) { setError('Candidate ID missing'); return null; }
    const key = `${file.name}-${file.size}-${file.lastModified}`;
    setUploadingIds(prev => new Set(prev).add(key));
    try {
      const material = await uploadCandidateMaterial(candidateId, file, signal);
      return material;
    } catch (e: any) {
      setError(e?.message || 'Upload failed');
      return null;
    } finally {
      setUploadingIds(prev => { const n = new Set(prev); n.delete(key); return n; });
    }
  }

  return { upload, uploadingIds, error };
}

export function useDeleteCandidateMaterial(candidateId: string | null) {
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);

  async function remove(materialId: string): Promise<boolean> {
    if (!candidateId) { setError('Candidate ID missing'); return false; }
    setDeletingIds(prev => new Set(prev).add(materialId));
    try {
      await deleteCandidateMaterial(candidateId, materialId);
      return true;
    } catch (e: any) {
      setError(e?.message || 'Delete failed');
      return false;
    } finally {
      setDeletingIds(prev => { const n = new Set(prev); n.delete(materialId); return n; });
    }
  }

  return { remove, deletingIds, error };
}
