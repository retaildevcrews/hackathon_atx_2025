// Central API endpoint resolution so all modules stay consistent.
// Priority: explicit decision kit var -> criteria var -> window globals -> default.
export function resolveApiBase(): string {
  // Prefer explicit env (works in Jest via process.env and can be inlined by Vite define).
  const procBase = typeof process !== 'undefined'
    ? (process.env.VITE_DECISION_API_URL || process.env.VITE_CRITERIA_API_URL)
    : undefined;
  const win: any = typeof window !== 'undefined' ? window : {};
  const winBase = win.__DECISION_API_URL__ || win.__CRITERIA_API_URL__;
  return procBase || winBase || 'http://localhost:8000';
}
