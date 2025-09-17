import { useState } from 'react';
import { createCandidate } from '../api/candidates';
import { Candidate } from '../types/candidates';

export function useCreateCandidate() {
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function create(input: { name: string; description?: string; decisionKitId: string }): Promise<Candidate | null> {
    setCreating(true); setError(null);
    try {
      const c = await createCandidate(input);
      return c;
    } catch (e: any) {
      setError(e?.message || 'Failed to create candidate');
      return null;
    } finally { setCreating(false); }
  }

  return { create, creating, error };
}
