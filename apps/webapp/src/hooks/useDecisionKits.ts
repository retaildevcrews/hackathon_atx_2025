import { useCallback, useEffect, useState } from 'react';
import { DecisionKitListItem } from '../types/decisionKits';
import { fetchDecisionKits, addKitToCacheList, removeKitFromCacheList } from '../api/decisionKits';

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

  const addKit = (kit: DecisionKitListItem) => setData(prev => addKitToCacheList(prev, kit));
  const removeKit = (id: string) => setData(prev => removeKitFromCacheList(prev, id));

  return { kits: data, loading, error, retry, addKit, removeKit, setKits: setData };
}
