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
export function clearDecisionKitCache() { detailCache.clear(); }

export function getDecisionKitsApiBase() { return API_BASE; }
