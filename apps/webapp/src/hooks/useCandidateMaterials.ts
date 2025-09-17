import { useCallback, useEffect, useState } from 'react';
import { CandidateMaterial } from '../types/candidates';
import { fetchCandidateMaterials } from '../api/candidates';

export function useCandidateMaterials(candidateId: string | null) {
  const [materials, setMaterials] = useState<CandidateMaterial[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshIndex, setRefreshIndex] = useState(0);

  const load = useCallback(async () => {
    if (!candidateId) return;
    setLoading(true); setError(null);
    try {
      const list = await fetchCandidateMaterials(candidateId);
      setMaterials(list);
    } catch (e: any) {
      setError(e?.message || 'Failed to load materials');
    } finally { setLoading(false); }
  }, [candidateId]);

  useEffect(() => { load(); }, [load, refreshIndex]);
  const refresh = () => setRefreshIndex(i => i + 1);

  return { materials, loading, error, refresh, setMaterials };
}
