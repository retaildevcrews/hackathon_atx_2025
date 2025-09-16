export interface DecisionKitListItem { id: string; name: string; description?: string }
export interface DecisionKitCandidate { id: string; name: string; description?: string }
export interface RubricCriterionEntry { criteria_id: string | number; weight: number; name?: string; description?: string; definition?: string }
export interface RubricSummary { id: string; name: string; description?: string; version: number; published: boolean; criteria: RubricCriterionEntry[] }
export interface DecisionKitDetail extends DecisionKitListItem {
	rubric?: RubricSummary; // may be absent; use rubric metadata to fetch
	rubricId?: string;
	rubricVersion?: string | number;
	rubricPublished?: boolean;
	candidates: DecisionKitCandidate[];
}

export type DecisionKit = DecisionKitDetail; // convenience alias
