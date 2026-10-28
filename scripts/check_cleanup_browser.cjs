// Block proposed cleanup paths only inside an isolated test browser.
const {chromium} = require('playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');

(async () => {
  const audit = JSON.parse(fs.readFileSync('qa/cleanup-audit.json', 'utf8'));
  const targets = new Set(audit.candidates.filter(c => c.references.length === 0).map(c => '/' + c.path));
  const browser = await chromium.launch({headless: true});
  const context = await browser.newContext({serviceWorkers: 'block'});
  const blocked = new Set();
  const errors = [];
  await context.route('**/*', route => {
    if (targets.has(decodeURIComponent(new URL(route.request().url()).pathname))) {
      blocked.add(route.request().url());
      return route.abort();
    }
    return route.continue();
  });
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(e.message));
  const checked = [];
  for (const width of [1440, 390]) {
    await page.setViewportSize({width, height: 1000});
    for (const path of audit.routes) {
      const response = await page.goto('https://www.igraphito.com' + path, {waitUntil: 'networkidle'});
      assert.equal(response.status(), 200, path);
      await page.locator('img').evaluateAll(async images => {
        images.forEach(image => image.loading = 'eager');
        await Promise.all(images.map(image => image.decode()));
      });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, path + ': overflow');
      assert.equal(await page.locator('h1').count(), 1, path);
      if (path === '/') await page.screenshot({path: `qa/cleanup-live-home-${width}.png`, fullPage: true});
      checked.push({path, width});
    }
  }
  assert.equal(blocked.size, 0, 'Candidate files are still requested');
  assert.deepEqual(errors, []);
  audit.browser = {status: 'passed', checked, blocked_requests: [...blocked], page_errors: errors};
  fs.writeFileSync('qa/cleanup-audit.json', JSON.stringify(audit, null, 2));
  await browser.close();
  console.log(`PASS: ${audit.routes.length} live routes at desktop and mobile widths; no candidate requests, missing images or page errors. Hosting unchanged.`);
})().catch(e => {console.error(e); process.exit(1);});
