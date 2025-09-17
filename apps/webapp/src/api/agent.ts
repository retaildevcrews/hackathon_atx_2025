import axios from 'axios';

// Create a local axios client using relative baseURL so Vite proxy can forward to /agent
const agentApi = axios.create({
  baseURL: '/',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

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
  const res = await agentApi.post<EvaluationResponseData>('/agent/evaluation/evaluate', payload);
  return res.data;
}
