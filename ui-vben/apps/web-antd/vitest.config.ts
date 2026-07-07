import { fileURLToPath } from 'node:url';

import { defineConfig } from 'vitest/config';

// Minimal vitest setup for the web-antd app.
//
// We only unit-test pure logic (e.g. helpers in src/utils) that has no
// component-rendering or DOM dependency, so a plain `node` environment is
// enough — no jsdom, no full app build. This keeps the tests fast and avoids
// the jiti/build issues associated with rendering Vue SFCs.
export default defineConfig({
  resolve: {
    // Honour the `#/*` subpath imports declared in package.json so that any
    // tested module using `#/...` resolves correctly.
    alias: {
      '#': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    environment: 'node',
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    // Keep output concise but clear.
    reporter: ['dot'],
  },
});
