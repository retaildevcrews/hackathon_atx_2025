import { useCallback, useEffect, useState } from 'react';
import { DecisionKitListItem } from '../types/decisionKits';
import { fetchDecisionKits } from '../api/decisionKits';

export function useDecisionKits() {
  const [data, setData] = useState<DecisionKitListItem[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryIndex, setRetryIndex] = useState(0);

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const kits = await fetchDecisionKits();
      setData(kits);
    } catch (e: any) {
      setError(e?.message || 'Failed to load decision kits');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load, retryIndex]);

  const retry = () => setRetryIndex((i: number) => i + 1);

  return { kits: data, loading, error, retry };
}
