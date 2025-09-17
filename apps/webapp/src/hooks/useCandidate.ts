import { useCallback, useEffect, useState } from 'react';
import { Candidate } from '../types/candidates';
import { fetchCandidate } from '../api/candidates';

export function useCandidate(candidateId: string | null) {
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryIndex, setRetryIndex] = useState(0);

  const load = useCallback(async () => {
    if (!candidateId) return;
    setLoading(true); setError(null);
    try {
      const c = await fetchCandidate(candidateId);
      setCandidate(c);
    } catch (e: any) {
      setError(e?.message || 'Failed to load candidate');
    } finally { setLoading(false); }
  }, [candidateId]);

  useEffect(() => { load(); }, [load, retryIndex]);
  const retry = () => setRetryIndex(i => i + 1);

  return { candidate, loading, error, retry, setCandidate };
}
