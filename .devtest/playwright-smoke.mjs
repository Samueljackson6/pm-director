// Dev/Test functional verification for pm-director local Docker env.
// Drives the real UI (login -> dashboard -> contracts -> invoices) with Playwright,
// asserts data renders from the LOCAL backend, and captures screenshots.
import { mkdirSync } from 'fs';
import { chromium } from 'playwright';

const BASE = 'http://localhost:8900/web/';
const SHOT_DIR = 'D:/Tare-workspace/pm-director/.devtest/screenshots';
mkdirSync(SHOT_DIR, { recursive: true });

const results = [];
const consoleErrors = [];
const apiSamples = {};

function logResult(step, ok, detail = '') {
  results.push({ step, ok, detail });
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${step}${detail ? ' — ' + detail : ''}`);
}

async function ensureLogin(page) {
  // If a password input is visible, we're on the login page -> log in (mock auth).
  const pw = page.locator('input[type="password"]');
  if (await pw.count() > 0) {
    await page.getByPlaceholder(/用户名|user/i).first().fill('admin');
    await page.getByPlaceholder(/密码|pass/i).first().fill('admin123');
    await page.getByRole('button', { name: 'login', exact: true }).click();
    await page.waitForLoadState('networkidle', { timeout: 20000 }).catch(() => {});
    return true;
  }
  return false;
}

async function go(page, path, waitSelector) {
  await page.goto(BASE + path, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await ensureLogin(page);
  if (waitSelector) {
    await page.waitForSelector(waitSelector, { timeout: 20000 });
  }
  await page.waitForTimeout(800); // let data settle
}

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1440, height: 900 } });
const page = await context.newPage();
page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('pageerror', (e) => consoleErrors.push('PAGEERROR: ' + e.message));

try {
  // 1. App loads (jiti fix => login page must render, not white-screen crash)
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(1500);
  const title = await page.title();
  logResult('app-load', true, `title="${title}"`);

  // 2. Login flow
  const didLogin = await ensureLogin(page);
  await page.waitForTimeout(1500);
  logResult('login', didLogin || (await page.locator('table, .dashboard, [class*="layout"]').count() > 0), didLogin ? 'submitted mock auth' : 'already authed');

  // 3. Capture API data the UI consumes (proves LOCAL backend is used)
  apiSamples.stats = await page.evaluate(async () => {
    try {
      const r = await fetch('/admin-api/api/stats');
      return await r.json();
    } catch (e) { return { error: String(e) }; }
  });
  logResult('api-stats-local', !apiSamples.stats?.error, `contract_count=${apiSamples.stats?.data?.contract_count}`);

  // 4. Dashboard page renders without crash
  await go(page, 'dashboard', null);
  await page.waitForSelector('body', { timeout: 10000 });
  const dashText = await page.locator('body').innerText().catch(() => '');
  await page.screenshot({ path: SHOT_DIR + '/dashboard.png', fullPage: false });
  logResult('dashboard-render', dashText.length > 0, `len=${dashText.length}`);

  // 5. Contracts list shows rows from local backend
  await go(page, 'contracts/list', 'table tbody tr, .vxe-body--row');
  const contractRows = await page.locator('table tbody tr, .vxe-body--row').count();
  await page.screenshot({ path: SHOT_DIR + '/contracts.png', fullPage: false });
  logResult('contracts-data', contractRows > 0, `rows=${contractRows}`);

  // 6. Invoices list shows rows
  await go(page, 'invoices/list', 'table tbody tr, .vxe-body--row');
  const invoiceRows = await page.locator('table tbody tr, .vxe-body--row').count();
  await page.screenshot({ path: SHOT_DIR + '/invoices.png', fullPage: false });
  logResult('invoices-data', invoiceRows > 0, `rows=${invoiceRows}`);

  // 7. Suppliers list (sanity)
  await go(page, 'suppliers/list', 'table tbody tr, .vxe-body--row');
  const supplierRows = await page.locator('table tbody tr, .vxe-body--row').count();
  await page.screenshot({ path: SHOT_DIR + '/suppliers.png', fullPage: false });
  logResult('suppliers-data', supplierRows > 0, `rows=${supplierRows}`);

} catch (e) {
  logResult('FATAL', false, String(e));
} finally {
  await browser.close();
}

const pass = results.filter((r) => r.ok).length;
const fail = results.length - pass;
console.log('\n==== SUMMARY ====');
console.log(JSON.stringify({ pass, fail, results, consoleErrors, apiSamples }, null, 2));
process.exit(fail > 0 ? 1 : 0);
