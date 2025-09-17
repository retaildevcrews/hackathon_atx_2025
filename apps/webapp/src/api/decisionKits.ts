import axios from 'axios';
import { DecisionKitListItem, DecisionKitDetail } from '../types/decisionKits';
import { resolveApiBase } from '../config/api';

const API_BASE = resolveApiBase();

const api = axios.create({
  baseURL: API_BASE,
  timeout: 8000,
  headers: { 'Content-Type': 'application/json' }
});

// In-memory cache for details keyed by string id (UUID)
const detailCache = new Map<string, DecisionKitDetail>();

export async function fetchDecisionKits(): Promise<DecisionKitListItem[]> {
  console.debug('[decisionKits] fetchDecisionKits');
  const res = await api.get<DecisionKitListItem[]>('/decision-kits/');
  return res.data;
}

export async function fetchDecisionKit(id: string): Promise<DecisionKitDetail> {
  console.debug('[decisionKits] fetchDecisionKit', id);
  if (!id || typeof id !== 'string') {
    throw new Error(`Invalid decision kit id: ${id}`);
  }
  if (detailCache.has(id)) return detailCache.get(id)!;
  const res = await api.get<DecisionKitDetail>(`/decision-kits/${encodeURIComponent(id)}`);
  detailCache.set(id, res.data);
  return res.data;
}

export function primeDecisionKitCache(kit: DecisionKitDetail) { detailCache.set(kit.id, kit); }
export function hasDecisionKitDetail(id: string) { return detailCache.has(id); }
export function clearDecisionKitCache() { detailCache.clear(); }

export function getDecisionKitsApiBase() { return API_BASE; }

// Create a decision kit
export interface CreateDecisionKitInput { name: string; description?: string; rubricId: string; candidateIds?: string[] }
export async function createDecisionKit(input: CreateDecisionKitInput): Promise<DecisionKitListItem> {
  if (!input.name || !input.name.trim()) throw new Error('Name is required');
  if (!input.rubricId) throw new Error('Rubric is required');
  const payload = {
    name: input.name.trim(),
    description: input.description?.trim() || undefined,
    rubricId: input.rubricId,
    candidateIds: input.candidateIds || []
  };
  const res = await api.post<DecisionKitListItem>('/decision-kits/', payload);
  return res.data;
}

// Delete a decision kit (cascade handled server-side)
export async function deleteDecisionKit(id: string): Promise<void> {
  if (!id) throw new Error('id required');
  await api.delete(`/decision-kits/${encodeURIComponent(id)}`);
  // On delete, remove any cached detail
  detailCache.delete(id);
}

// Lightweight cache mutation helpers for list consumers (caller maintains list)
export function addKitToCacheList(local: DecisionKitListItem[] | null, kit: DecisionKitListItem): DecisionKitListItem[] {
  const arr = local ? [...local] : [];
  // Avoid duplicates
  if (!arr.find(k => k.id === kit.id)) arr.unshift(kit);
  return arr;
}

export function removeKitFromCacheList(local: DecisionKitListItem[] | null, id: string): DecisionKitListItem[] | null {
  if (!local) return local;
  return local.filter(k => k.id !== id);

}

// Assign a rubric to a decision kit and return the updated kit
export async function assignRubricToDecisionKit(kitId: string, rubricId: string): Promise<DecisionKitDetail> {
  if (!kitId || !rubricId) throw new Error('kitId and rubricId are required');
  const res = await api.patch<DecisionKitDetail>(`/decision-kits/${encodeURIComponent(kitId)}`, { rubricId });
  const updated = res.data;
  detailCache.set(updated.id, updated);
  return updated;
}
