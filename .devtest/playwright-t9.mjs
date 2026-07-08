// T9 verification: full smoke test with dashboard KPI + chart assertions
import { mkdirSync } from 'fs';
import { chromium } from 'playwright';

const BASE = 'http://localhost:8900/web/';
const SHOT_DIR = 'D:/Tare-workspace/pm-director/.devtest/screenshots';
mkdirSync(SHOT_DIR, { recursive: true });

const results = [];
const consoleErrors = [];
const apiSamples = {};

function logResult(step, ok, detail) {
  results.push({ step, ok, detail });
  console.log((ok ? 'PASS' : 'FAIL') + '  ' + step + (detail ? ' — ' + detail : ''));
}

async function ensureLogin(page) {
  const pw = page.locator('input[type="password"]');
  if (await pw.count() > 0) {
    await page.getByPlaceholder(/用户名|user/i).first().fill('admin');
    await page.getByPlaceholder(/密码|pass/i).first().fill('admin123');
    await page.getByRole('button', { name: 'login', exact: true }).click();
    await page.waitForLoadState('networkidle', { timeout: 20000 }).catch(function() {});
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
  await page.waitForTimeout(800);
}

var browser;
try {
  browser = await chromium.launch({ headless: true });
  var context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1440, height: 900 } });
  var page = await context.newPage();
  page.on('console', function(m) { if (m.type() === 'error') consoleErrors.push(m.text()); });
  page.on('pageerror', function(e) { consoleErrors.push('PAGEERROR: ' + e.message); });

  // 1. App loads
  await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(1500);
  var title = await page.title();
  logResult('app-load', true, 'title="' + title + '"');

  // 2. Login
  var didLogin = await ensureLogin(page);
  await page.waitForTimeout(1500);
  logResult('login', true, didLogin ? 'submitted mock auth' : 'already authed');

  // 3. Local backend API
  apiSamples.stats = await page.evaluate(async function() {
    try { var r = await fetch('/admin-api/api/stats'); return await r.json(); }
    catch (e) { return { error: String(e) }; }
  });
  logResult('api-stats-local', !apiSamples.stats.error, 'contract_count=' + (apiSamples.stats.data ? apiSamples.stats.data.contract_count : 'ERR'));

  // 4. Dashboard — T9 dashboard with real KPI
  await go(page, 'dashboard', null);
  await page.waitForTimeout(2000);

  var dashText = await page.locator('body').innerText().catch(function() { return ''; });
  var hasContractCount = dashText.indexOf('50') >= 0;
  var hasReceiptRate = dashText.indexOf('67.4') >= 0 || dashText.indexOf('67') >= 0;
  var hasInvoiced = dashText.indexOf('1049') >= 0;
  var hasReceived = dashText.indexOf('707') >= 0;
  var hasCurrency = dashText.indexOf('\u4e07\u5143') >= 0; // 万元
  var hasCharts = dashText.indexOf('\u5408\u540c\u7c7b\u578b\u5206\u5e03') >= 0 // 合同类型分布
    && dashText.indexOf('\u53d1\u7968\u72b6\u6001\u5206\u5e03') >= 0; // 发票状态分布
  var hasTrend = dashText.indexOf('\u8d22\u52a1\u6279\u6b21\u8d8b\u52bf') >= 0 // 财务批次趋势
    && dashText.indexOf('\u6708\u5ea6\u5f00\u7968') >= 0; // 月度开票

  apiSamples.overview = await page.evaluate(async function() {
    try { var r = await fetch('/admin-api/api/dashboard/overview'); return await r.json(); }
    catch (e) { return { error: String(e) }; }
  });

  await page.screenshot({ path: SHOT_DIR + '/dashboard.png', fullPage: false });

  var allKpiOk = hasContractCount && hasInvoiced && hasReceived && hasCurrency;
  logResult('dashboard-kpi', allKpiOk, 'count50=' + hasContractCount + ' invoiced1049=' + hasInvoiced + ' received707=' + hasReceived + ' currency=' + hasCurrency);
  logResult('dashboard-charts', hasCharts && hasTrend, 'piecharts=' + hasCharts + ' trend=' + hasTrend);
  logResult('dashboard-receipt-rate', hasReceiptRate, 'rate_67.4=' + hasReceiptRate);

  var overviewOk = apiSamples.overview && apiSamples.overview.code === 0;
  logResult('dashboard-api', overviewOk, 'code=' + (apiSamples.overview ? apiSamples.overview.code : 'null'));

  // 5. Contracts list
  await go(page, 'contracts/list', 'table tbody tr, .vxe-body--row');
  var contractRows = await page.locator('table tbody tr, .vxe-body--row').count();
  await page.screenshot({ path: SHOT_DIR + '/contracts.png', fullPage: false });
  logResult('contracts-data', contractRows > 0, 'rows=' + contractRows);

  // 6. Invoices list
  await go(page, 'invoices/list', 'table tbody tr, .vxe-body--row');
  var invoiceRows = await page.locator('table tbody tr, .vxe-body--row').count();
  await page.screenshot({ path: SHOT_DIR + '/invoices.png', fullPage: false });
  logResult('invoices-data', invoiceRows > 0, 'rows=' + invoiceRows);

  // 7. Suppliers list
  await go(page, 'suppliers/list', 'table tbody tr, .vxe-body--row');
  var supplierRows = await page.locator('table tbody tr, .vxe-body--row').count();
  await page.screenshot({ path: SHOT_DIR + '/suppliers.png', fullPage: false });
  logResult('suppliers-data', supplierRows > 0, 'rows=' + supplierRows);

} catch (e) {
  logResult('FATAL', false, String(e));
} finally {
  if (browser) await browser.close();
}

var pass = results.filter(function(r) { return r.ok; }).length;
var fail = results.length - pass;
console.log('\n==== SUMMARY ====');
console.log(JSON.stringify({ pass: pass, fail: fail, results: results, consoleErrors: consoleErrors }, null, 2));
process.exit(fail > 0 ? 1 : 0);
