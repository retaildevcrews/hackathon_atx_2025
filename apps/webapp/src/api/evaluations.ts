import axios from 'axios';
import { resolveApiBase } from '../config/api';
import { EvaluationResultSummary, EvaluationResult } from '../types/evaluations';

const API_BASE = resolveApiBase();

const api = axios.create({
  baseURL: API_BASE,
  timeout: 8000
});

function normalizeError(err: any): Error {
  const detail = err?.response?.data?.detail;
  if (detail) {
    const e = new Error(detail);
    (e as any).code = err?.response?.status;
    return e;
  }
  return err instanceof Error ? err : new Error('Request failed');
}

export async function fetchCandidateEvaluations(candidateId: string): Promise<EvaluationResultSummary[]> {
  if (!candidateId) throw new Error('candidateId required');
  try {
    const res = await api.get<EvaluationResultSummary[]>(`/candidates/${encodeURIComponent(candidateId)}/evaluations`);
    return res.data || [];
  } catch (err: any) {
    throw normalizeError(err);
  }
}

export async function fetchEvaluationResult(evaluationId: string): Promise<EvaluationResult> {
  if (!evaluationId) throw new Error('evaluationId required');
  try {
    const res = await api.get<EvaluationResult>(`/candidates/evaluations/${encodeURIComponent(evaluationId)}`);
    return res.data as EvaluationResult;
  } catch (err: any) {
    throw normalizeError(err);
  }
}
