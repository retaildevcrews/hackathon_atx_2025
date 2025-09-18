import { useEffect, useRef, useState, useCallback } from 'react';
import { EvaluationResultSummary } from '../types/evaluations';
import { fetchCandidateEvaluations } from '../api/evaluations';

interface HookState {
  summaries: EvaluationResultSummary[];
  latest: EvaluationResultSummary | null;
  loading: boolean;
  error: string | null;
  retry: () => void;
  refresh: () => Promise<void>;
}

// Simple in-memory cache to avoid repeat fetches in a session
const summaryCache = new Map<string, { time: number; summaries: EvaluationResultSummary[] }>();
const CACHE_TTL_MS = 60_000; // 1 minute (can adjust later)

function selectLatest(summaries: EvaluationResultSummary[]): EvaluationResultSummary | null {
  if (!summaries || summaries.length === 0) return null;
  return summaries.reduce((a, b) => (new Date(b.created_at).getTime() > new Date(a.created_at).getTime() ? b : a));
}

export function useCandidateEvaluations(candidateId: string | null | undefined): HookState {
  const [summaries, setSummaries] = useState<EvaluationResultSummary[]>([]);
  const [latest, setLatest] = useState<EvaluationResultSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(!!candidateId);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const load = useCallback(async (force?: boolean) => {
    if (!candidateId) return;
    const now = Date.now();
    const cached = summaryCache.get(candidateId);
    if (!force && cached && now - cached.time < CACHE_TTL_MS) {
      setSummaries(cached.summaries);
      setLatest(selectLatest(cached.summaries));
      setLoading(false);
      return;
    }
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchCandidateEvaluations(candidateId);
      summaryCache.set(candidateId, { time: Date.now(), summaries: data });
      setSummaries(data);
      setLatest(selectLatest(data));
    } catch (e: any) {
      if (e.name === 'CanceledError' || e.name === 'AbortError') return; // ignore aborts
      setError(e?.message || 'Failed to load evaluations');
    } finally {
      setLoading(false);
    }
  }, [candidateId]);

  useEffect(() => {
    load();
    return () => {
      abortRef.current?.abort();
    };
  }, [load]);

  const retry = useCallback(() => load(true), [load]);

  const refresh = useCallback(async () => {
    await load(true);
  }, [load]);

  return { summaries, latest, loading, error, retry, refresh };
}

export function invalidateCandidateEvaluations(candidateId: string) {
  summaryCache.delete(candidateId);
}
