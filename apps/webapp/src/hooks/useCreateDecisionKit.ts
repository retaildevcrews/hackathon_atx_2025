import { useState, useCallback } from 'react';
import { createDecisionKit, CreateDecisionKitInput, addKitToCacheList } from '../api/decisionKits';
import { DecisionKitListItem } from '../types/decisionKits';

export interface UseCreateDecisionKitOptions {
  onSuccess?: (kit: DecisionKitListItem) => void;
  onError?: (err: any) => void;
  getList?: () => DecisionKitListItem[] | null; // optional accessor to mutate local list
  setList?: (next: DecisionKitListItem[] | null) => void;
}

export function useCreateDecisionKit(opts: UseCreateDecisionKitOptions = {}) {
  const { onSuccess, onError, getList, setList } = opts;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mutate = useCallback(async (input: CreateDecisionKitInput) => {
    setLoading(true); setError(null);
    try {
      const kit = await createDecisionKit(input);
      if (getList && setList) {
        const current = getList();
        setList(addKitToCacheList(current, kit));
      }
      onSuccess?.(kit);
      return kit;
    } catch (e: any) {
      const msg = e?.response?.data?.message || e?.message || 'Failed to create decision kit';
      setError(msg);
      onError?.(e);
      throw e;
    } finally {
      setLoading(false);
    }
  }, [getList, setList, onSuccess, onError]);

  return { createDecisionKit: mutate, loading, error };
}
