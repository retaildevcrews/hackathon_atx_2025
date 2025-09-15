import { useCallback, useEffect, useState } from 'react';
import axios from 'axios';

export interface Criteria {
  id?: string;
  name: string;
  description: string;
  definition: string;
}

const API_BASE = import.meta.env.VITE_CRITERIA_API_URL || 'http://localhost:8000';

export function useCriteria() {
  const [criteria, setCriteria] = useState<Criteria[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const res = await axios.get<Criteria[]>(`${API_BASE}/criteria/`);
      setCriteria(res.data);
    } catch (e: any) {
      setError(e.message || 'Failed to load');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const create = useCallback(async (data: Omit<Criteria, 'id'>) => {
    const res = await axios.post<Criteria>(`${API_BASE}/criteria/`, data);
    setCriteria(prev => [res.data, ...prev]);
  }, []);

  const remove = useCallback(async (id: string) => {
    await axios.delete(`${API_BASE}/criteria/${id}`);
    setCriteria(prev => prev.filter(c => c.id !== id));
  }, []);

  return { criteria, loading, error, refresh: fetchAll, create, remove };
}
