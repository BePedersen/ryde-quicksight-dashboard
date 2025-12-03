import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  timeout: 120000,
  expect: { timeout: 15000 },
  reporter: [['list']],
  use: {
    headless: process.env.HEADLESS !== 'false',
    viewport: { width: 1366, height: 768 },
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) PlaywrightScraper/1.0 Chrome/118 Safari/537.36',
    ignoreHTTPSErrors: true,
    screenshot: 'only-on-failure',
    video: 'off',
    baseURL: process.env.TARGET_URL || undefined
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } }
  ]
});