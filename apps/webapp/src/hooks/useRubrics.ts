import { useCallback, useEffect, useState } from 'react';
import { Rubric } from '../types/rubric';
import { fetchRubricsList } from '../api/rubrics';

export function useRubrics() {
  const [rubrics, setRubrics] = useState<Rubric[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryIndex, setRetryIndex] = useState(0);

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const data = await fetchRubricsList();
      setRubrics(data);
    } catch (e: any) {
      setError(e?.message || 'Failed to load rubrics');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load, retryIndex]);
  const retry = () => setRetryIndex(i => i + 1);

  return { rubrics, loading, error, retry };
}
