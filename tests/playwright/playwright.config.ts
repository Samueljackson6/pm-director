import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './',
  timeout: 60000,
  expect: {
    timeout: 10000,
  },
  use: {
    baseURL: 'http://localhost:18090',
    headless: true,
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        browserName: 'chromium',
        viewport: { width: 1440, height: 720 },
      },
    },
  ],
});
