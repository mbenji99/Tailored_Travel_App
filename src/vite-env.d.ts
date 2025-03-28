/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_URL: string;
    // Add other custom env variables here
    // readonly VITE_OTHER_VAR: string;
  }
  
  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
  