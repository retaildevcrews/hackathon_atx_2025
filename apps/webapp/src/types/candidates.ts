export interface Candidate {
  id: string;
  name: string;
  description?: string;
  decisionKitId?: string;
}

export interface CandidateMaterial {
  id: string;
  name: string; // server returns stored filename
  type?: string; // mime or extension if provided
  url?: string; // optional download / viewing URL
}

export interface CandidateMaterialList {
  items: CandidateMaterial[];
}

export interface CreateCandidateInput {
  name: string;
  description?: string;
  decisionKitId: string; // required for association ordering server-side
}
