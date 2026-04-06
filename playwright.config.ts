import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './generated_tests',
  timeout: 30000,
  retries: 0,
  use: {
    baseURL: 'http://localhost:3000', // change to your app URL
    headless: true,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});
