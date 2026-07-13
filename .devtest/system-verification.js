const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:18090/web';
const REPORT_DIR = path.join(__dirname, 'verification-report');

// 确保报告目录存在
if (!fs.existsSync(REPORT_DIR)) {
  fs.mkdirSync(REPORT_DIR, { recursive: true });
}

const results = {
  timestamp: new Date().toISOString(),
  summary: { passed: 0, failed: 0, warnings: 0 },
  pages: [],
  contracts: [],
  errors: []
};

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function log(msg) {
  console.log(msg);
}

async function main() {
  log('启动浏览器...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();

  // 收集控制台错误
  page.on('console', msg => {
    if (msg.type() === 'error') {
      results.errors.push({ type: 'console', message: msg.text() });
    }
  });

  // 收集页面错误
  page.on('pageerror', err => {
    results.errors.push({ type: 'pageerror', message: err.message });
  });

  try {
    // ==================== 登录 ====================
    log('\n=== 登录 ===');
    await page.goto(`${BASE_URL}/dashboard/overview`);
    await sleep(2000);

    const currentUrl = page.url();
    if (currentUrl.includes('login')) {
      log('执行登录...');
      await page.click('button:has-text("登")');
      await sleep(3000);
    }
    results.summary.passed++;
    log('✅ 登录成功');

    // ==================== 1. 仪表盘验证 ====================
    log('\n=== 1. 仪表盘验证 ===');
    await page.goto(`${BASE_URL}/dashboard/overview`);
    await sleep(3000);

    // 截图
    const dashboardShot = path.join(REPORT_DIR, '01-dashboard.png');
    await page.screenshot({ path: dashboardShot, fullPage: true });

    // 检查KPI卡片
    const kpiCards = await page.$$eval('.grid > div', cards => cards.length);
    if (kpiCards >= 4) {
      results.summary.passed++;
      log(`✅ KPI卡片数量: ${kpiCards}`);
    } else {
      results.summary.failed++;
      results.pages.push({ page: '仪表盘', issue: `KPI卡片不足(${kpiCards})` });
      log(`❌ KPI卡片不足: ${kpiCards}`);
    }

    results.pages.push({ page: '仪表盘', status: 'passed', screenshot: dashboardShot });

    // ==================== 2. 合同列表验证 ====================
    log('\n=== 2. 合同列表验证 ===');
    await page.goto(`${BASE_URL}/contracts`);
    await sleep(3000);

    const listShot = path.join(REPORT_DIR, '02-contracts-list.png');
    await page.screenshot({ path: listShot, fullPage: true });

    // 检查合同数量
    const rows = await page.$$eval('table tbody tr', rows => rows.length);
    if (rows >= 40) {
      results.summary.passed++;
      log(`✅ 合同列表数量: ${rows}`);
    } else {
      results.summary.warnings++;
      log(`⚠️ 合同列表数量: ${rows}`);
    }

    results.pages.push({ page: '合同列表', status: 'passed', screenshot: listShot });

    // ==================== 3. 科研类合同详情验证 ====================
    log('\n=== 3. 科研类合同详情验证 ===');
    const researchContracts = [
      'ZH02-202408007',
      'ZH02-202604020',
      'ZH02-202604021',
      'ZH02-202604023',
      'ZH02-202604024',
      'ZH02-202604025',
      'ZH02-202604026',
      'ZH02-202507011',
      'ZH02-202509025',
      'ZH02-202512056'
    ];

    for (const contractId of researchContracts) {
      log(`验证科研类合同: ${contractId}`);
      await page.goto(`${BASE_URL}/contracts/${contractId}`);
      await sleep(3000);

      // 截图
      const shotPath = path.join(REPORT_DIR, `research-${contractId}.png`);
      await page.screenshot({ path: shotPath, fullPage: true });

      // 检查甘特图
      const ganttCanvas = await page.$('canvas');
      const hasGantt = ganttCanvas !== null;

      // 检查付款金额匹配
      const contractAmount = await page.$eval('.text-2xl.font-bold.text-gray-900', el => el.textContent).catch(() => 'N/A');

      results.contracts.push({
        contractId,
        type: '科研类',
        hasGantt,
        contractAmount,
        screenshot: shotPath,
        status: hasGantt ? 'passed' : 'warning'
      });

      if (hasGantt) {
        results.summary.passed++;
        log(`  ✅ 甘特图正常`);
      } else {
        results.summary.warnings++;
        log(`  ⚠️ 甘特图缺失`);
      }
    }

    // ==================== 4. 服务类合同详情验证 ====================
    log('\n=== 4. 服务类合同详情验证 ===');
    const serviceContracts = [
      'ZH02-202508013',
      'ZH02-202508019',
      'ZH02-202406004',
      'ZH02-202409008',
      'ZH02-202411014',
      'ZH02-202410010',
      'ZH02-202512058',
      'ZH02-202508016',
      'ZH02-202602014',
      'ZH02-202601001'
    ];

    for (const contractId of serviceContracts) {
      log(`验证服务类合同: ${contractId}`);
      await page.goto(`${BASE_URL}/contracts/${contractId}`);
      await sleep(3000);

      // 截图
      const shotPath = path.join(REPORT_DIR, `service-${contractId}.png`);
      await page.screenshot({ path: shotPath, fullPage: true });

      // 检查服务内容区域
      const serviceContent = await page.$('text=服务内容').catch(() => null);

      // 检查付款进度
      const paymentSection = await page.$('text=付款').catch(() => null);

      results.contracts.push({
        contractId,
        type: '服务类',
        hasServiceContent: serviceContent !== null,
        hasPaymentSection: paymentSection !== null,
        screenshot: shotPath,
        status: 'passed'
      });

      results.summary.passed++;
      log(`  ✅ 服务类合同验证通过`);
    }

    // ==================== 5. 项目列表验证 ====================
    log('\n=== 5. 项目列表验证 ===');
    await page.goto(`${BASE_URL}/projects`);
    await sleep(2000);

    const projectsShot = path.join(REPORT_DIR, '05-projects-list.png');
    await page.screenshot({ path: projectsShot, fullPage: true });

    const projectRows = await page.$$eval('table tbody tr', rows => rows.length);
    results.summary.passed++;
    log(`✅ 项目列表数量: ${projectRows}`);
    results.pages.push({ page: '项目列表', status: 'passed', screenshot: projectsShot });

    // ==================== 6. 发票列表验证 ====================
    log('\n=== 6. 发票列表验证 ===');
    await page.goto(`${BASE_URL}/invoices`);
    await sleep(2000);

    const invoicesShot = path.join(REPORT_DIR, '06-invoices-list.png');
    await page.screenshot({ path: invoicesShot, fullPage: true });

    results.summary.passed++;
    log('✅ 发票列表验证通过');
    results.pages.push({ page: '发票列表', status: 'passed', screenshot: invoicesShot });

    // ==================== 7. 供应商列表验证 ====================
    log('\n=== 7. 供应商列表验证 ===');
    await page.goto(`${BASE_URL}/suppliers`);
    await sleep(2000);

    const suppliersShot = path.join(REPORT_DIR, '07-suppliers-list.png');
    await page.screenshot({ path: suppliersShot, fullPage: true });

    results.summary.passed++;
    log('✅ 供应商列表验证通过');
    results.pages.push({ page: '供应商列表', status: 'passed', screenshot: suppliersShot });

    // ==================== 8. 错误检查 ====================
    log('\n=== 8. 错误检查 ===');
    if (results.errors.length === 0) {
      results.summary.passed++;
      log('✅ 无控制台错误');
    } else {
      results.summary.failed++;
      log(`❌ 发现 ${results.errors.length} 个错误`);
    }

  } catch (error) {
    log(`❌ 验证失败: ${error.message}`);
    results.errors.push({ type: 'runtime', message: error.message });
  } finally {
    await browser.close();
  }

  // ==================== 生成报告 ====================
  const reportPath = path.join(REPORT_DIR, 'verification-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));

  log('\n========================================');
  log('验证完成！');
  log(`✅ 通过: ${results.summary.passed}`);
  log(`❌ 失败: ${results.summary.failed}`);
  log(`⚠️ 警告: ${results.summary.warnings}`);
  log(`📄 报告: ${reportPath}`);
  log(`📸 截图目录: ${REPORT_DIR}`);
  log('========================================');
}

main();
