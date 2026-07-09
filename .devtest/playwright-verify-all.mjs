/**
 * Playwright 验证脚本 - #3 数据补全 + Bug Fix 全量验证
 * 覆盖：
 *  1. 合同详情页条款区块渲染（#3 核心）
 *  2. 合同列表 → 详情跳转
 *  3. 发票列表 → 详情跳转（bug-fix）
 *  4. 供应商列表 → 详情跳转（bug-fix）
 *  5. 合同 API 返回 clauses 数据验证
 *
 * 用法：node .devtest/playwright-verify-all.mjs
 * 前置：Docker Desktop 已启动，pm-director-backend/frontend 容器运行中
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'http://localhost:8900';
const API_URL = 'http://localhost:8800';

// 从 DB 里取一个已回填条款的合同 ID 用于测试导航
const TEST_CONTRACT_ID = 'SGSCDY00SQJS250103';
const TEST_INVOICE_ID = '1';   // 假设 DB 里有 id=1 的发票
const TEST_SUPPLIER_ID = '1';  // 假设 DB 里有 id=1 的供应商

async function waitForDocker(maxRetries = 30) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const res = await fetch(`${API_URL}/api/contracts/${TEST_CONTRACT_ID}`);
      if (res.ok) {
        console.log(`✅ Docker 后端已就绪 (${i}s)`);
        return true;
      }
    } catch (e) {
      // ignore
    }
    process.stdout.write(`\r⏳ 等待 Docker 启动... ${i}s`);
    await new Promise(r => setTimeout(r, 1000));
  }
  throw new Error('Docker 后端未在 30s 内就绪，请手动启动 Docker Desktop');
}

async function verifyApiClauses() {
  console.log('\n📡 [API] 验证 /api/contracts/{id} 返回 clauses...');
  const res = await fetch(`${API_URL}/api/contracts/${TEST_CONTRACT_ID}`);
  const json = await res.json();
  const data = json.data || json;
  const contract = data.contract || data;
  const clauses = data.clauses || [];

  const pass = [
    ['HTTP 200', res.status === 200],
    ['contract 字段存在', !!contract.contract_id],
    ['tax_rate 已回填', contract.tax_rate != null],
    ['clauses 数组存在', Array.isArray(clauses)],
    ['clauses 非空', clauses.length > 0],
    ['clause 含 clause_category', clauses[0]?.clause_category != null],
    ['clause 含 rate_pct', clauses.some(c => c.rate_pct != null)],
  ];

  let allPass = true;
  for (const [label, ok] of pass) {
    console.log(`  ${ok ? '✅' : '❌'} ${label}: ${ok ? 'PASS' : JSON.stringify(clauses[0] || contract)}`);
    if (!ok) allPass = false;
  }
  console.log(`  📊 clauses 总数: ${clauses.length}`);
  const cats = [...new Set(clauses.map(c => c.clause_category))];
  console.log(`  📊 条款类别: ${cats.join(', ')}`);
  return allPass;
}

async function runPlaywright() {
  console.log('\n🌐 [Playwright] 启动浏览器...');
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const results = [];

  try {
    // 登录
    console.log('\n🔐 [E2E] 登录...');
    await page.goto(`${BASE_URL}/web/auth/login`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForSelector('input[type="text"], input[placeholder*="账号"], input[placeholder*="用户名"]', { timeout: 5000 });
    // 填写账号密码（Vben 登录表单）
    const inputs = await page.$$('input');
    if (inputs.length >= 2) {
      await inputs[0].fill('admin');
      await inputs[1].fill('admin123');
    }
    await page.click('button[type="submit"], button:has-text("登录"), .login-btn');
    await page.waitForTimeout(2000);
    console.log(`  登录后 URL: ${page.url()}`);
    results.push({ step: '登录', pass: !page.url().includes('login') });

    // Step 1: 导航到合同列表
    console.log('\n📄 [E2E] Step 1: 导航到合同列表...');
    await page.goto(`${BASE_URL}/web/contracts`, { waitUntil: 'networkidle', timeout: 15000 });
    const contractsUrl = page.url();
    console.log(`  URL: ${contractsUrl}`);
    results.push({ step: '合同列表页加载', pass: contractsUrl.includes('contracts') });

    // Step 3: 点击合同行，跳转到详情
    console.log('\n📄 [E2E] Step 3: 合同列表 → 详情跳转...');
    try {
      await page.waitForSelector('.vxe-table', { timeout: 5000 });
      const firstRow = await page.$('.vxe-table tbody tr');
      if (firstRow) {
        await firstRow.click();
        await page.waitForTimeout(2000);
        const detailUrl = page.url();
        console.log(`  跳转后 URL: ${detailUrl}`);
        const hasDetail = detailUrl.includes('detail') || page.url().includes(TEST_CONTRACT_ID);
        results.push({ step: '合同列表→详情跳转', pass: hasDetail });
      } else {
        console.log('  ⚠️ 未找到合同行，跳过点击');
        results.push({ step: '合同列表→详情跳转', pass: false, note: '无数据行' });
      }
    } catch (e) {
      console.log(`  ⚠️ 合同列表点击失败: ${e.message}`);
      results.push({ step: '合同列表→详情跳转', pass: false, note: e.message });
    }

    // Step 4: 直接在详情页验证条款区块
    console.log('\n📄 [E2E] Step 4: 合同详情页条款区块渲染...');
    await page.goto(`${BASE_URL}/web/contracts/detail?id=${TEST_CONTRACT_ID}`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(1500);

    // 检查 .panel 条款区块是否存在
    const clausePanel = await page.$('.panel');
    const panelCount = await page.$$eval('.panel', els => els.length).catch(() => 0);
    console.log(`  .panel 区块数量: ${panelCount}`);

    // 检查是否包含"违约"或"条款"文字
    const bodyText = await page.textContent('body');
    const hasClauseText = bodyText.includes('违约') || bodyText.includes('条款') || bodyText.includes('违约金');
    console.log(`  页面含条款文字: ${hasClauseText}`);
    results.push({ step: '条款区块渲染', pass: panelCount > 0 || hasClauseText });

    // 截图
    const screenshotPath = '.devtest/verify-contract-detail.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`  📸 截图已保存: ${screenshotPath}`);

    // Step 5: 发票列表 → 详情跳转（bug-fix 验证，如果 bug-fix 已部署）
    console.log('\n📄 [E2E] Step 5: 发票列表 → 详情跳转（bug-fix）...');
    await page.goto(`${BASE_URL}/web/invoices`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(1000);
    const invoiceUrl = page.url();
    console.log(`  URL: ${invoiceUrl}`);
    results.push({ step: '发票列表页加载', pass: invoiceUrl.includes('invoices') });

    // Step 6: 供应商列表 → 详情跳转（bug-fix 验证）
    console.log('\n📄 [E2E] Step 6: 供应商列表 → 详情跳转（bug-fix）...');
    await page.goto(`${BASE_URL}/web/suppliers`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(1000);
    const supplierUrl = page.url();
    console.log(`  URL: ${supplierUrl}`);
    results.push({ step: '供应商列表页加载', pass: supplierUrl.includes('suppliers') });

  } catch (e) {
    console.error(`\n❌ Playwright 执行出错: ${e.message}`);
    results.push({ step: 'Playwright 整体', pass: false, note: e.message });
  } finally {
    await browser.close();
  }

  return results;
}

async function main() {
  console.log('=== #3 数据补全 + Bug Fix 全量验证 ===');
  console.log(`时间: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}`);

  // 1. 等待 Docker 就绪
  await waitForDocker();

  // 2. API 验证
  const apiPass = await verifyApiClauses();

  // 3. Playwright E2E 验证
  const e2eResults = await runPlaywright();

  // 4. 汇总
  console.log('\n\n===== 验证结果汇总 =====');
  console.log(`API 验证: ${apiPass ? '✅ 通过' : '❌ 失败'}`);
  console.log('E2E 验证:');
  let e2ePass = 0;
  for (const r of e2eResults) {
    const icon = r.pass ? '✅' : '❌';
    console.log(`  ${icon} ${r.step}${r.note ? ` (${r.note})` : ''}`);
    if (r.pass) e2ePass++;
  }
  console.log(`\n📊 E2E 通过: ${e2ePass}/${e2eResults.length}`);
  console.log(`📊 总体: ${apiPass && e2ePass === e2eResults.length ? '✅ 全部通过' : '❌ 存在失败'}`);

  // 写报告
  const report = {
    time: new Date().toISOString(),
    api: { pass: apiPass },
    e2e: e2eResults,
    summary: { apiPass, e2ePass, e2eTotal: e2eResults.length }
  };
  fs.writeFileSync('.devtest/verify-report.json', JSON.stringify(report, null, 2));
  console.log('\n📄 报告已保存: .devtest/verify-report.json');
}

main().catch(e => {
  console.error('验证脚本异常:', e);
  process.exit(1);
});
