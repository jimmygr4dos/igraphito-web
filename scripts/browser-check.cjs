const { chromium } = require('playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');

async function main() {
  const base = process.env.PREVIEW_URL || 'http://127.0.0.1:8080';
  const routes = JSON.parse(fs.readFileSync('dist/routes.json', 'utf8'));
  fs.mkdirSync('qa', { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const errors = [];
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.on('pageerror', error => errors.push(error.message));
  for (const route of routes) {
    const response = await page.goto(base + route);
    assert.equal(response.status(), 200, route);
    assert.equal(await page.locator('h1').count(), 1, route);
    assert.equal(await page.locator('form').count(), 0, route);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `${route}: desktop overflow`);
  }
  await page.goto(base + '/');
  await page.locator('img').evaluateAll(images => images.forEach(image => image.loading = 'eager'));
  await page.evaluate(async () => { await Promise.all(Array.from(document.images, image => image.decode())); });
  await page.screenshot({ path: 'qa/home-desktop.png', fullPage: true });
  assert.equal(await page.locator('.client-logo').count(), 24);
  await page.locator('[data-carousel-toggle]').click();
  assert.equal(await page.locator('[data-carousel-toggle]').getAttribute('aria-pressed'), 'true');
  await page.locator('[data-carousel-next]').click();
  await page.waitForFunction(() => document.querySelector('.carousel-track').scrollLeft > 0);
  const textFits = await page.locator('[data-carousel-toggle]').evaluate(el => el.scrollWidth <= el.clientWidth && el.scrollHeight <= el.clientHeight);
  assert.equal(textFits, true, 'Carousel rotation control must fit its text');
  await page.setViewportSize({ width: 390, height: 844 });
  assert.equal(await page.locator('#primary-nav').isVisible(), false);
  await page.locator('[data-nav-toggle]').click();
  assert.equal(await page.locator('#primary-nav').isVisible(), true);
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('#primary-nav').isVisible(), false);
  assert.equal(await page.locator('[data-nav-toggle]').getAttribute('aria-expanded'), 'false');
  for (const route of routes) {
    await page.goto(base + route);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `${route}: mobile overflow`);
    assert.equal(await page.locator('a.whatsapp-float').isVisible(), true);
  }
  await page.goto(base + '/');
  await page.screenshot({ path: 'qa/home-mobile.png', fullPage: true });
  await page.goto(base + '/papeleria-corporativa/');
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.screenshot({ path: 'qa/category-desktop.png', fullPage: true });
  await page.goto(base + '/productos/cuadernos-corporativos/');
  await page.screenshot({ path: 'qa/product-desktop.png', fullPage: true });
  const reduced = await browser.newPage({ reducedMotion: 'reduce' });
  await reduced.goto(base + '/');
  assert.equal(await reduced.locator('[data-carousel-toggle]').isDisabled(), true);
  const nojs = await browser.newPage({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  await nojs.goto(base + '/');
  assert.equal(await nojs.locator('#primary-nav').isVisible(), true);
  assert.equal(await nojs.locator('[data-carousel-next]').isVisible(), false);
  assert.equal(await nojs.locator('a.whatsapp-float').isVisible(), true);
  assert.equal(await nojs.locator('a.whatsapp-float').getAttribute('href').then(href => href.startsWith('https://wa.me/51942722449?text=')), true);
  await nojs.screenshot({ path: 'qa/home-no-js.png', fullPage: true });
  await page.goto(base + '/contacto/');
  await page.evaluate(() => { window.gtag = () => { throw new Error('simulated unavailable analytics'); }; });
  const href = await page.locator('a.whatsapp-float').getAttribute('href');
  assert.equal(href.includes('51942722449'), true);
  await page.route('https://wa.me/**', route => route.fulfill({ status: 200, contentType: 'text/html', body: '<title>Simulated WhatsApp destination</title>' }));
  await page.locator('a.whatsapp-float').click();
  await page.waitForURL('https://wa.me/**');
  assert.equal(page.url().startsWith('https://wa.me/51942722449?text='), true, 'Contact navigation survives analytics errors');
  assert.equal(errors.length, 0, errors.join('\n'));
  await browser.close();
  fs.writeFileSync('qa/report.json', JSON.stringify({ status: 'passed', routes: routes.length, viewports: ['1440x1000', '390x844'], checks: ['HTTP routes', 'one H1', 'no forms', 'no overflow', 'menu and Escape', 'carousel controls', 'reduced motion', 'no JavaScript fallback', 'WhatsApp contact', 'no page errors'] }, null, 2));
  console.log('PASS: browser checks for all 29 routes, desktop/mobile, reduced motion and no-JS.');
}
main().catch(error => { console.error(error); process.exit(1); });
