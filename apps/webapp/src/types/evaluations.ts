// Evaluation related TypeScript interfaces mirroring backend models

export interface EvaluationResultSummary {
  id: string;
  rubric_id: string;
  rubric_name: string;
  overall_score: number;
  total_candidates: number;
  is_batch: boolean;
  created_at: string; // ISO timestamp
}

export interface EvaluationCandidate {
  id: string;
  evaluation_id: string;
  candidate_id: string;
  candidate_score: number;
  rank?: number | null;
  created_at: string;
}

export interface EvaluationCriteriaScore {
  criteria_id?: string;
  criteria_name?: string;
  score?: number;
  weight?: number;
  weighted_score?: number;
  explanation?: string;
  // Allow arbitrary extras
  [key: string]: any;
}

export interface EvaluationIndividualResult {
  candidate_id?: string;
  overall_score?: number;
  criteria?: EvaluationCriteriaScore[]; // assumed list if provided
  // Allow arbitrary extras
  [key: string]: any;
}

export interface EvaluationResult extends EvaluationResultSummary {
  individual_results: (EvaluationIndividualResult | any)[]; // keep loose but prefer typed shape
  comparison_summary?: any;
  evaluation_metadata?: Record<string, any> | null;
  updated_at: string;
  candidates: EvaluationCandidate[];
}

export interface CandidateEvaluationsResponse {
  // Backend returns raw array (per route definition with response_model=List[EvaluationResultSummary])
  // This interface exists for future compatibility if wrapped.
  items?: EvaluationResultSummary[];
}
