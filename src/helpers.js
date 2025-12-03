export async function waitForAnySelector(page, candidates, opts = {}) {
  const list = candidates.split(',').map(s => s.trim()).filter(Boolean);
  for (const selector of list) {
    try {
      await page.waitForSelector(selector, { state: 'visible', timeout: opts.timeout ?? 8000 });
      return selector;
    } catch (_) { }
  }
  throw new Error(`Ingen av kandidat-selektorene dukket opp: ${candidates}`);
}

export async function safeClick(page, selector) {
  await page.waitForSelector(selector, { state: 'visible', timeout: 10000 });
  await page.click(selector, { delay: 20 });
}

export async function typeAndEnter(page, selector, value) {
  await page.waitForSelector(selector, { state: 'visible', timeout: 10000 });
  await page.fill(selector, value, { timeout: 10000 });
}

export async function dumpArtifacts(page, tag = 'after') {
  await page.screenshot({ path: `./${Date.now()}-${tag}.png`, fullPage: true });
  const html = await page.content();
  await BunWriteFile(`./${Date.now()}-${tag}.html`, html);
}

async function BunWriteFile(p, data) {
  const { writeFile } = await import('node:fs/promises');
  await writeFile(p, data);
}