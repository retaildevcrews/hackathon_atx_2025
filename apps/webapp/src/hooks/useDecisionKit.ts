import { useCallback, useEffect, useState } from 'react';
import { DecisionKitDetail } from '../types/decisionKits';
import { fetchDecisionKit } from '../api/decisionKits';

export function useDecisionKit(id: string | null) {
  const [data, setData] = useState<DecisionKitDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryIndex, setRetryIndex] = useState(0);

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true); setError(null);
    try {
      const kit = await fetchDecisionKit(id);
      setData(kit);
    } catch (e: any) {
      setError(e?.message || 'Failed to load decision kit');
    } finally { setLoading(false); }
  }, [id]);

  useEffect(() => { load(); }, [load, retryIndex]);
  const retry = () => setRetryIndex((i: number) => i + 1);

  return { kit: data, loading, error, retry };
}
