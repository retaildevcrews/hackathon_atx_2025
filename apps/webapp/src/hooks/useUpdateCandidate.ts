import { useState } from 'react';
import { updateCandidate } from '../api/candidates';
import { Candidate } from '../types/candidates';

export function useUpdateCandidate(candidateId: string | null) {
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function update(input: { name: string; description?: string; decisionKitId?: string }): Promise<Candidate | null> {
    if (!candidateId) {
      setError('candidate id required');
      return null;
    }
    setUpdating(true); setError(null);
    try {
      const c = await updateCandidate(candidateId, input);
      return c;
    } catch (e: any) {
      setError(e?.message || 'Failed to update candidate');
      return null;
    } finally { setUpdating(false); }
  }

  return { update, updating, error };
}
