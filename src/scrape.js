import 'dotenv/config';
import { chromium } from 'playwright';
import { waitForAnySelector, safeClick, typeAndEnter, dumpArtifacts } from './helpers.js';

const {
  TARGET_URL,
  HEADLESS,
  USERNAME,
  PASSWORD,
  SEL_USERNAME,
  SEL_PASSWORD,
  SEL_SUBMIT,
  READY_SELECTOR
} = process.env;

if (!TARGET_URL) {
  console.error('Mangler TARGET_URL i .env');
  process.exit(1);
}

async function main() {
  const browser = await chromium.launch({
    headless: HEADLESS !== 'false',
    args: ['--disable-dev-shm-usage', '--no-sandbox']
  });

  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) PlaywrightScraper/1.0 Chrome/118 Safari/537.36',
    viewport: { width: 1366, height: 768 },
    ignoreHTTPSErrors: true
  });

  const page = await ctx.newPage();

  page.on('response', async (resp) => {
    if (resp.status() >= 400) {
      console.warn('⚠️  HTTP', resp.status(), resp.url());
    }
  });

  console.log('Navigerer til:', TARGET_URL);
  const resp = await page.goto(TARGET_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
  if (!resp || !resp.ok()) console.warn('Advarsel: Første svar ikke OK, fortsetter...');

  if (USERNAME && PASSWORD) {
    if (!SEL_USERNAME || !SEL_PASSWORD || !SEL_SUBMIT) {
      throw new Error('Innlogging aktivert, men selektorer mangler i .env');
    }
    console.log('Forsøker innlogging...');
    const userSel = await waitForAnySelector(page, SEL_USERNAME);
    await typeAndEnter(page, userSel, USERNAME);

    const passSel = await waitForAnySelector(page, SEL_PASSWORD);
    await typeAndEnter(page, passSel, PASSWORD);

    const submitSel = await waitForAnySelector(page, SEL_SUBMIT);
    await safeClick(page, submitSel);

    await page.waitForLoadState('domcontentloaded', { timeout: 30000 });
  }

  if (READY_SELECTOR) {
    console.log('Venter på READY_SELECTOR:', READY_SELECTOR);
    const readySel = await waitForAnySelector(page, READY_SELECTOR, { timeout: 20000 });
    console.log('Klar selektor funnet:', readySel);
  } else {
    await page.waitForLoadState('networkidle', { timeout: 30000 });
  }

  const title = await page.title();
  const finalUrl = page.url();
  console.log('Tittel:', title);
  console.log('Endelig URL:', finalUrl);

  await dumpArtifacts(page, 'ready');
  await browser.close();
}

main().catch(err => {
  console.error('❌ Feil i scraper:', err?.message || err);
  process.exit(1);
});