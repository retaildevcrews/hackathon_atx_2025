import { useCallback, useEffect, useState } from 'react';
import axios from 'axios';

export interface Criteria {
  id?: string;
  name: string;
  description: string;
  definition: string;
}

const API_BASE = (import.meta as any).env?.VITE_CRITERIA_API_URL || (window as any).__CRITERIA_API_URL__ || 'http://localhost:8000';

// Single axios instance with basic timeout + JSON headers
const api = axios.create({
  baseURL: API_BASE,
  timeout: 8000,
  headers: { 'Content-Type': 'application/json' }
});

// Simple helper to classify network vs HTTP errors
function mapError(err: any): string {
  if (err?.response) return `HTTP ${err.response.status}`;
  if (err?.request) return 'Network unreachable';
  return err?.message || 'Unknown error';
}

export function useCriteria() {
  const [criteria, setCriteria] = useState<Criteria[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const res = await api.get<Criteria[]>(`/criteria/`);
      setCriteria(res.data);
    } catch (e: any) {
      const msg = mapError(e);
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const create = useCallback(async (data: Omit<Criteria, 'id'>) => {
    const res = await api.post<Criteria>(`/criteria/`, data);
    setCriteria(prev => [res.data, ...prev]);
  }, []);

  const remove = useCallback(async (id: string) => {
    await api.delete(`/criteria/${id}`);
    setCriteria(prev => prev.filter(c => c.id !== id));
  }, []);

  return { criteria, loading, error, refresh: fetchAll, create, remove, apiBase: API_BASE };
}
