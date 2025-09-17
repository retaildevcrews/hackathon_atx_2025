import { useState, useCallback } from 'react';
import { deleteDecisionKit, removeKitFromCacheList } from '../api/decisionKits';
import { DecisionKitListItem } from '../types/decisionKits';

export interface UseDeleteDecisionKitOptions {
  onSuccess?: (id: string) => void;
  onError?: (err: any) => void;
  getList?: () => DecisionKitListItem[] | null;
  setList?: (next: DecisionKitListItem[] | null) => void;
}

export function useDeleteDecisionKit(opts: UseDeleteDecisionKitOptions = {}) {
  const { onSuccess, onError, getList, setList } = opts;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mutate = useCallback(async (id: string) => {
    setLoading(true); setError(null);
    try {
      await deleteDecisionKit(id);
      if (getList && setList) {
        const current = getList();
        setList(removeKitFromCacheList(current, id));
      }
      onSuccess?.(id);
    } catch (e: any) {
      const status = e?.response?.status;
      if (status === 404) {
        // treat as already deleted
        if (getList && setList) {
          const current = getList();
          setList(removeKitFromCacheList(current, id));
        }
        onSuccess?.(id);
        return;
      }
      const msg = status === 409 ? 'Decision kit is locked and cannot be deleted.' : (e?.message || 'Failed to delete decision kit');
      setError(msg);
      onError?.(e);
      throw e;
    } finally {
      setLoading(false);
    }
  }, [getList, setList, onSuccess, onError]);

  return { deleteDecisionKit: mutate, loading, error };
}
