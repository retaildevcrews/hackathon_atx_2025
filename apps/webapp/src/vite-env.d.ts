/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_CRITERIA_API_URL?: string;
  readonly VITE_AGENT_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
