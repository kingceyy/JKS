// @lovable.dev/vite-tanstack-config already includes the following — do NOT add them manually
// or the app will break with duplicate plugins:
//   - tanstackStart, viteReact, tailwindcss, tsConfigPaths, cloudflare (build-only),
//     componentTagger (dev-only), VITE_* env injection, @ path alias, React/TanStack dedupe,
//     error logger plugins, and sandbox detection (port/host/strictPort).
// You can pass additional config via defineConfig({ vite: { ... } }) if needed.import { defineConfig } from 'vite'// @lovable.dev/vite-tanstack-config already includes everything
// Do NOT add plugins manually (react, tailwind, tsconfigPaths, etc.)
import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  // Tu peux ajouter des options supplémentaires ici si besoin
  build: {
    outDir: 'dist',
  },
});
