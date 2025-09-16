import axios from 'axios';

export interface CriteriaRecord {
  id: string;
  name: string;
  description?: string;
  definition?: string;
}

const base = import.meta.env.VITE_API_BASE_URL || '/api';
const client = axios.create({ baseURL: base });

const criteriaCache = new Map<string, CriteriaRecord>();
let listCache: CriteriaRecord[] | null = null;

export async function fetchAllCriteria(force?: boolean): Promise<CriteriaRecord[]> {
  if (listCache && !force) return listCache;
  const resp = await client.get<CriteriaRecord[]>('/criteria/');
  listCache = resp.data;
  for (const c of listCache) criteriaCache.set(c.id, c);
  return listCache;
}

export async function fetchCriteria(id: string): Promise<CriteriaRecord | null> {
  if (criteriaCache.has(id)) return criteriaCache.get(id)!;
  try {
    const resp = await client.get<CriteriaRecord>(`/criteria/${id}`);
    criteriaCache.set(id, resp.data);
    return resp.data;
  } catch (e: any) {
    if (e.response && e.response.status === 404) return null;
    throw e;
  }
}

export function clearCriteriaCache() {
  listCache = null;
  criteriaCache.clear();
}
