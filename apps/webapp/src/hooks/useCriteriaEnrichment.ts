import { useEffect, useState } from 'react';
import { fetchAllCriteria, CriteriaRecord } from '../api/criteria';
import type { RubricCriterionEntry } from '../types/decisionKits';

interface Enriched extends RubricCriterionEntry {
  description?: string;
  definition?: string;
}

export function useCriteriaEnrichment(entries: RubricCriterionEntry[] | undefined) {
  const [data, setData] = useState<Enriched[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      if (!entries || entries.length === 0) {
        setData([]);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const list = await fetchAllCriteria();
        if (cancelled) return;
  const map = new Map<string, CriteriaRecord>();
  list.forEach(c => map.set(String(c.id), c));
        const enriched: Enriched[] = entries.map(e => {
          const criteriaId = (e as any).criteria_id ?? (e as any).id ?? (e as any).criteriaId;
          const weight = (e as any).weight ?? (e as any).score ?? 0;
          const match = map.get(String(criteriaId)) || null;
          return {
            ...e,
            criteria_id: criteriaId,
            weight,
            description: (e as any).description || match?.description,
            definition: (e as any).definition || match?.definition,
          };
        });
        setData(enriched);
      } catch (err: any) {
        if (cancelled) return;
        setError(err.message || 'Failed to enrich criteria');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    run();
    return () => { cancelled = true; };
  }, [entries]);

  return { enriched: data, loading, error };
}
