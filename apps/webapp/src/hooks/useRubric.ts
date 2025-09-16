import { useState, useEffect } from 'react';
import { Rubric } from '../types/rubric';

const API_URL = '/api/rubrics';

export function useRubric() {
  const [rubrics, setRubrics] = useState<Rubric[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRubrics();
  }, []);

  async function fetchRubrics() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(API_URL);
      const data = await res.json();
      setRubrics(data);
    } catch (err) {
      setError('Failed to fetch rubrics');
    } finally {
      setLoading(false);
    }
  }

  async function createRubric(rubric: Omit<Rubric, 'id'>) {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rubric),
      });
      const newRubric = await res.json();
  setRubrics((prev: Rubric[]) => [...prev, newRubric]);
      return newRubric;
    } catch (err) {
      setError('Failed to create rubric');
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function updateRubric(id: string, rubric: Partial<Rubric>) {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rubric),
      });
      const updated = await res.json();
  setRubrics((prev: Rubric[]) => prev.map((r: Rubric) => r.id === id ? updated : r));
      return updated;
    } catch (err) {
      setError('Failed to update rubric');
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function deleteRubric(id: string) {
    setLoading(true);
    setError(null);
    try {
      await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
  setRubrics((prev: Rubric[]) => prev.filter((r: Rubric) => r.id !== id));
    } catch (err) {
      setError('Failed to delete rubric');
      throw err;
    } finally {
      setLoading(false);
    }
  }

  return {
    rubrics,
    loading,
    error,
    fetchRubrics,
    createRubric,
    updateRubric,
    deleteRubric,
  };
}
