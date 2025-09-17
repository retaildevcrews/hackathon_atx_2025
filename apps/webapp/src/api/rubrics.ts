import axios from 'axios';
import { resolveApiBase } from '../config/api';
import { RubricSummary } from '../types/decisionKits';
import { Rubric, Criteria } from '../types/rubric';
import { CriteriaRecord } from './criteria';

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

/**
 * Create a new rubric
 */
export async function createRubric(rubric: Partial<Rubric>): Promise<Rubric> {
  if (!rubric.name?.trim()) throw new Error('Rubric name is required');

  const res = await api.post<Rubric>('/rubrics/', {
    name: rubric.name.trim(),
    description: rubric.description?.trim() || '',
    criteria: rubric.criteria || []
  });

  // Clear cache to ensure fresh data on next fetch
  clearRubricCache();
  return res.data;
}

/**
 * Update an existing rubric
 */
export async function updateRubric(id: string, updates: Partial<Rubric>): Promise<Rubric> {
  if (!id) throw new Error('Rubric ID is required');

  const res = await api.put<Rubric>(`/rubrics/${encodeURIComponent(id)}`, {
    ...(updates.name && { name: updates.name.trim() }),
    ...(updates.description !== undefined && { description: updates.description.trim() }),
    ...(updates.criteria && { criteria: updates.criteria })
  });

  // Clear cache to ensure fresh data
  clearRubricCache();
  return res.data;
}

/**
 * Delete a rubric
 */
export async function deleteRubric(id: string): Promise<void> {
  if (!id) throw new Error('Rubric ID is required');

  await api.delete(`/rubrics/${encodeURIComponent(id)}`);

  // Clear cache to ensure fresh data
  clearRubricCache();
}

/**
 * Fetch detailed rubric information with criteria
 */
export async function fetchRubricDetail(id: string): Promise<Rubric> {
  if (!id) throw new Error('Missing rubric id');
  const res = await api.get<Rubric>(`/rubrics/${encodeURIComponent(id)}`);
  return res.data;
}

/**
 * Fetch available criteria for rubric composition
 */
export async function fetchAvailableCriteria(): Promise<CriteriaRecord[]> {
  const res = await api.get<CriteriaRecord[]>('/criteria/');
  return res.data;
}

export function clearRubricCache() { rubricCache.clear(); }
