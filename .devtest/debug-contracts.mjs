import { mkdirSync } from 'fs';
import { chromium } from 'playwright';

const BASE = 'http://localhost:8900/web/';
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const errs = [];
page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
page.on('pageerror', (e) => errs.push('PAGEERROR: ' + e.message));

async function ensureLogin() {
  const pw = page.locator('input[type="password"]');
  if (await pw.count() > 0) {
    await page.getByPlaceholder(/用户名|user/i).first().fill('admin');
    await page.getByPlaceholder(/密码|pass/i).first().fill('admin123');
    await page.getByRole('button', { name: 'login', exact: true }).click();
    await page.waitForLoadState('networkidle').catch(() => {});
  }
}

await page.goto(BASE, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(1500);
await ensureLogin();
await page.waitForTimeout(1500);

const urlBefore = page.url();
await page.goto(BASE + '#/contracts/list', { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(5000);
const urlAfter = page.url();

const bodyText = await page.locator('body').innerText().catch(() => '');
console.log('URL before:', urlBefore);
console.log('URL after :', urlAfter);
console.log('console errors:', JSON.stringify(errs, null, 2));
console.log('BODY TEXT (first 1200):\n', bodyText.slice(0, 1200));

const sels = ['.vxe-body--row', 'table tbody tr', '.vxe-table', '.vben-grid', '[class*="grid"]', '.ant-table-tbody tr', '.vxe-grid'];
for (const s of sels) {
  const n = await page.locator(s).count().catch(() => -1);
  console.log(`selector "${s}" -> count=${n}`);
}
await page.screenshot({ path: '/d/Tare-workspace/pm-director/.devtest/screenshots/debug-contracts.png', fullPage: true });
await browser.close();
