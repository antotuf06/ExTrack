import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

// In development the SPA runs on Vite (5173) and proxies /api to the backend.
// In production the backend serves frontend/dist directly.
export default defineConfig({
  plugins: [svelte()],
  server: {
    host: "127.0.0.1",
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
