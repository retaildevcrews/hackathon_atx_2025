import axios from 'axios';
import { resolveApiBase } from '../config/api';
import { Candidate, CandidateMaterial, CandidateMaterialList, CreateCandidateInput, UpdateCandidateInput } from '../types/candidates';

const API_BASE = resolveApiBase();

const api = axios.create({
  baseURL: API_BASE,
  timeout: 8000
});

export async function createCandidate(input: CreateCandidateInput): Promise<Candidate> {
  if (!input.name?.trim()) throw new Error('Name is required');
  if (!input.decisionKitId) throw new Error('decisionKitId required');
  const payload = {
    name: input.name.trim(),
    description: input.description?.trim() || undefined,
    decisionKitId: input.decisionKitId
  };
  try {
    const res = await api.post<Candidate>('/candidates/', payload);
    return res.data;
  } catch (err: any) {
    const detail = err?.response?.data?.detail;
    if (detail) {
      const e = new Error(detail);
      (e as any).code = err?.response?.status;
      throw e;
    }
    throw err;
  }
}

export async function fetchCandidate(id: string): Promise<Candidate> {
  if (!id) throw new Error('candidate id required');
  const res = await api.get<Candidate>(`/candidates/${encodeURIComponent(id)}`);
  return res.data;
}

export async function fetchCandidateMaterials(candidateId: string): Promise<CandidateMaterial[]> {
  if (!candidateId) throw new Error('candidate id required');
  const res = await api.get<CandidateMaterialList>(`/candidates/${encodeURIComponent(candidateId)}/materials`);
  // backend returns { items: [...] }
  return (res.data as any)?.items || [];
}

export async function uploadCandidateMaterial(candidateId: string, file: File, signal?: AbortSignal): Promise<CandidateMaterial> {
  if (!candidateId) throw new Error('candidate id required');
  if (!file) throw new Error('file required');
  const form = new FormData();
  form.append('file', file, file.name);
  const res = await api.post<CandidateMaterial>(`/candidates/${encodeURIComponent(candidateId)}/materials`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    signal
  });
  return res.data;
}

export async function deleteCandidateMaterial(candidateId: string, materialId: string): Promise<void> {
  if (!candidateId || !materialId) throw new Error('ids required');
  await api.delete(`/candidates/${encodeURIComponent(candidateId)}/materials/${encodeURIComponent(materialId)}`);
}

// (Optional) delete candidate
export async function deleteCandidate(candidateId: string): Promise<void> {
  if (!candidateId) throw new Error('candidate id required');
  await api.delete(`/candidates/${encodeURIComponent(candidateId)}`);
}

export async function updateCandidate(candidateId: string, input: UpdateCandidateInput): Promise<Candidate> {
  if (!candidateId) throw new Error('candidate id required');
  if (!input.name?.trim()) throw new Error('Name is required');
  const payload: any = {
    name: input.name.trim(),
    description: input.description?.trim() || undefined,
  };
  if (input.decisionKitId) payload.decisionKitId = input.decisionKitId;
  try {
    const res = await api.put<Candidate>(`/candidates/${encodeURIComponent(candidateId)}`, payload);
    return res.data;
  } catch (err: any) {
    const detail = err?.response?.data?.detail;
    if (detail) {
      const e = new Error(detail);
      (e as any).code = err?.response?.status;
      throw e;
    }
    throw err;
  }
}
