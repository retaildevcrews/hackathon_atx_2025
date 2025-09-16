import axios from 'axios';
import { resolveApiBase } from '../config/api';
import { RubricSummary } from '../types/decisionKits';
import { Rubric } from '../types/rubric';

const API_BASE = resolveApiBase();
const api = axios.create({ baseURL: API_BASE, timeout: 8000, headers: { 'Content-Type': 'application/json' } });

const rubricCache = new Map<string, RubricSummary>();

export async function fetchRubricSummary(id: string): Promise<RubricSummary> {
  if (!id) throw new Error('Missing rubric id');
  if (rubricCache.has(id)) return rubricCache.get(id)!;
  const res = await api.get<RubricSummary>(`/rubrics/${encodeURIComponent(id)}`);
  rubricCache.set(id, res.data);
  return res.data;
}

export async function fetchRubricsList(): Promise<Rubric[]> {
  const res = await api.get<Rubric[]>('/rubrics/');
  return res.data;
}

export function clearRubricCache() { rubricCache.clear(); }
