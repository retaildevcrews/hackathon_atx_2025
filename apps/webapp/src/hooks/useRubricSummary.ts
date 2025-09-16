import { useCallback, useEffect, useState } from 'react';
import { fetchRubricSummary } from '../api/rubrics';
import { RubricSummary } from '../types/decisionKits';

export function useRubricSummary(rubricId?: string) {
  const [rubric, setRubric] = useState<RubricSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryIndex, setRetryIndex] = useState(0);

  const load = useCallback(async () => {
    if (!rubricId) return;
    setLoading(true); setError(null);
    try {
      const data = await fetchRubricSummary(rubricId);
      setRubric(data);
    } catch (e: any) {
      setError(e?.message || 'Failed to load rubric');
    } finally { setLoading(false); }
  }, [rubricId]);

  useEffect(() => { load(); }, [load, retryIndex]);
  const retry = () => setRetryIndex(i => i + 1);

  return { rubric, loading, error, retry };
}
