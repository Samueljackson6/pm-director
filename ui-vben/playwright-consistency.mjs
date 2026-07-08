// Consistency-fix verification for pm-director local Docker env.
// Covers: dashboard, contract detail (gantt canvas + finance token + upload),
// invoice detail, supplier detail (StateBlock). Drives the REAL UI + REAL local backend.
// NOTE: placed under ui-vben/ so `import { chromium } from 'playwright'` resolves from ui-vben/node_modules.
import { mkdirSync, writeFileSync } from 'fs';
import { chromium } from 'playwright';

const BASE = 'http://localhost:8900/web/';
const SHOT_DIR = 'D:/Tare-workspace/pm-director/.devtest/screenshots';
const TEST_FILE = 'D:/Tare-workspace/pm-director/.devtest/_upload_test.txt';
// 已知拥有带中文区间排期（'YYYY-MM 至 YYYY-MM'）的阶段，用于确定性验证甘特图渲染
const GANTT_CONTRACT = 'ZH02-202604024';
mkdirSync(SHOT_DIR, { recursive: true });
writeFileSync(TEST_FILE, 'pm-director upload smoke test\n');

const results = [];
const consoleErrors = [];
function logResult(step, ok, detail = '') {
  results.push({ step, ok, detail });
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${step}${detail ? ' — ' + detail : ''}`);
}

async function ensureLogin(page) {
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

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1440, height: 1000 } });
const page = await context.newPage();
page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('pageerror', (e) => consoleErrors.push('PAGEERROR: ' + e.message));
const failedReq = [];
page.on('response', (r) => { if (r.status() >= 400) failedReq.push(r.status() + ' ' + r.url()); });

try {
  // 1. Load + login
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(1500);
  await ensureLogin(page);
  await page.waitForTimeout(1200);
  logResult('app-login', true);

  // 2. Dashboard renders (KPI cards + at least one chart canvas)
  await page.goto(BASE + 'dashboard', { waitUntil: 'domcontentloaded' });
  await ensureLogin(page);
  await page.waitForSelector('text=综合看板', { timeout: 20000 }).catch(() => {});
  await page.waitForTimeout(1500);
  const dashCanvas = await page.locator('canvas').count();
  await page.screenshot({ path: SHOT_DIR + '/v2-dashboard.png' });
  logResult('dashboard-render', dashCanvas > 0, `chartCanvas=${dashCanvas}`);

  // 3. Contracts list -> open first contract detail (proves CellRouterLink jump)
  await page.goto(BASE + 'contracts', { waitUntil: 'domcontentloaded' });
  await ensureLogin(page);
  await page.waitForSelector('.vxe-body--row, table tbody tr', { timeout: 20000 });
  await page.waitForTimeout(800);
  await page.locator('.vxe-body--row').first().locator('span[title="点击查看详情"]').first().click();
  const jumpOk = await page.waitForSelector('text=合同详情', { timeout: 20000 }).then(() => true).catch(() => false);
  await page.waitForTimeout(1200);
  await page.screenshot({ path: SHOT_DIR + '/v2-contract-detail-listjump.png' });
  logResult('contract-list-jump', jumpOk);

  // 4. 深链到已知有排期的合同，确定性验证甘特图 canvas
  await page.goto(BASE + 'contracts/detail?id=' + GANTT_CONTRACT, { waitUntil: 'domcontentloaded' });
  await ensureLogin(page);
  const ganttText = await page.waitForSelector('text=阶段进度（甘特图）', { timeout: 20000 }).then(() => true).catch(() => false);
  await page.waitForTimeout(1500);
  const ganttCanvas = await page.locator('.ant-card:has-text("阶段进度") canvas').count();
  await page.screenshot({ path: SHOT_DIR + '/v2-contract-gantt.png' });
  logResult('contract-gantt-canvas', ganttText && ganttCanvas > 0, `ganttTitle=${ganttText} canvas=${ganttCanvas}`);

  // 5. Finance token color applied (inline var resolves to rgb(22,119,255))
  const finance = await page.evaluate(() => {
    const varDefined = getComputedStyle(document.documentElement).getPropertyValue('--finance-invoiced').trim();
    const el = document.querySelector('[style*="finance-invoiced"]');
    const elColor = el ? getComputedStyle(el).color : null;
    return { varDefined, elColor };
  });
  const tokenOk = finance.varDefined === '#1677ff' && finance.elColor === 'rgb(22, 119, 255)';
  logResult('finance-token-color', tokenOk, `var=${finance.varDefined} resolved=${finance.elColor}`);

  // 6. Upload a contract file (proves backend upload endpoint + frontend flow)
  const fileInput = page.locator('input[type="file"]').first();
  await fileInput.setInputFiles(TEST_FILE);
  let uploaded = false;
  for (let i = 0; i < 20; i++) {
    await page.waitForTimeout(500);
    if (await page.locator('.ant-card:has-text("合同文件") >> text=/_upload_test/').count() > 0) { uploaded = true; break; }
  }
  await page.screenshot({ path: SHOT_DIR + '/v2-contract-upload.png' });
  logResult('contract-file-upload', uploaded);

  // 7. Invoice list renders + detail (StateBlock) via deep-link
  await page.goto(BASE + 'invoices', { waitUntil: 'domcontentloaded' });
  await ensureLogin(page);
  await page.waitForSelector('.vxe-body--row', { timeout: 20000 }).catch(() => {});
  await page.waitForTimeout(800);
  const invRows = await page.locator('.vxe-body--row').count();
  logResult('invoice-list-render', invRows > 0, `rows=${invRows}`);
  await page.goto(BASE + 'invoices/detail?id=51', { waitUntil: 'domcontentloaded' });
  await ensureLogin(page);
  const invOk = await page.waitForSelector('text=发票详情', { timeout: 20000 }).then(() => true).catch(() => false);
  await page.waitForTimeout(1000);
  await page.screenshot({ path: SHOT_DIR + '/v2-invoice-detail.png' });
  logResult('invoice-detail-render', invOk);

  // 8. Supplier list renders + detail (StateBlock) via deep-link
  await page.goto(BASE + 'suppliers', { waitUntil: 'domcontentloaded' });
  await ensureLogin(page);
  await page.waitForSelector('.vxe-body--row', { timeout: 20000 }).catch(() => {});
  await page.waitForTimeout(800);
  const supRows = await page.locator('.vxe-body--row').count();
  logResult('supplier-list-render', supRows > 0, `rows=${supRows}`);
  await page.goto(BASE + 'suppliers/detail?id=SUP-64997', { waitUntil: 'domcontentloaded' });
  await ensureLogin(page);
  const supOk = await page.waitForSelector('text=供应商详情', { timeout: 20000 }).then(() => true).catch(() => false);
  await page.waitForTimeout(1000);
  await page.screenshot({ path: SHOT_DIR + '/v2-supplier-detail.png' });
  logResult('supplier-detail-render', supOk);

  // 9. No console errors
  logResult('no-console-errors', consoleErrors.length === 0, `count=${consoleErrors.length}`);

} catch (e) {
  logResult('FATAL', false, String(e));
} finally {
  await browser.close();
}

const pass = results.filter((r) => r.ok).length;
const fail = results.length - pass;
console.log('\n==== SUMMARY ====');
console.log(JSON.stringify({ pass, fail, results, consoleErrors: consoleErrors.slice(0, 20), failedRequests: failedReq.slice(0, 20) }, null, 2));
process.exit(fail > 0 ? 1 : 0);
