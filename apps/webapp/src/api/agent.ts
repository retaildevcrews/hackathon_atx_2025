import axios from 'axios';

export interface EvaluationRequestPayload {
  rubric_id: string;
  candidate_ids: string[];
}

export interface EvaluationResponseData {
  status: 'success' | 'error';
  is_batch: boolean;
  evaluation_id?: string;
  error?: string;
  // optional fields for fallback modes
  evaluation?: any;
  batch_result?: any;
}

export async function evaluateCandidates(rubricId: string, candidateIds: string[]): Promise<EvaluationResponseData> {
  if (!rubricId) throw new Error('rubricId is required');
  if (!candidateIds || candidateIds.length === 0) throw new Error('candidateIds is required');
  const payload: EvaluationRequestPayload = { rubric_id: rubricId, candidate_ids: candidateIds };
  // Determine base URL in a way that works for both Vite dev and Docker static build
  const env = (import.meta as any)?.env || {};
  const envBase: string | undefined = env.VITE_AGENT_BASE_URL;
  let base: string;
  if (envBase && typeof envBase === 'string' && envBase.trim()) {
    base = envBase.trim();
  } else if (env?.DEV) {
    // In Vite dev server, use proxy path
    base = '/agent';
  } else if (typeof window !== 'undefined') {
    // In production/static build, default to same host on port 8001
    const { protocol, hostname } = window.location;
    base = `${protocol}//${hostname}:8001`;
  } else {
    // Fallback for non-browser contexts
    base = 'http://localhost:8001';
  }
  const url = `${base.replace(/\/+$/, '')}/evaluation/evaluate`;
  const res = await axios.post<EvaluationResponseData>(url, payload, {
    headers: { 'Content-Type': 'application/json' },
    timeout: 15000,
  });
  return res.data;
}
