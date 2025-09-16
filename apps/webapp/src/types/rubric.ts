export interface Rubric {
  id: string;
  name: string;
  description: string;
  criteria: Criteria[];
}

export interface Criteria {
  id: string;
  name: string;
  description: string;
  definition: string;
}
