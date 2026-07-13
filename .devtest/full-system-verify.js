/**
 * 全面系统验证脚本
 * 覆盖所有功能和所有合同
 * 验证UI、功能、数据显示
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:18090/web';
const REPORT_DIR = path.join(__dirname, 'verification-report');

// 确保报告目录存在
if (!fs.existsSync(REPORT_DIR)) {
  fs.mkdirSync(REPORT_DIR, { recursive: true });
}

// 测试结果收集
const results = {
  startTime: new Date().toISOString(),
  summary: { total: 0, passed: 0, failed: 0, warnings: 0 },
  pages: [],
  contracts: [],
  errors: [],
  warnings: [],
};

// 辅助函数
async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function log(message, type = 'info') {
  const timestamp = new Date().toLocaleTimeString();
  const prefix = type === 'error' ? '❌' : type === 'warn' ? '⚠️' : '✅';
  console.log(`[${timestamp}] ${prefix} ${message}`);
}

// 获取所有合同ID
async function getAllContracts(page) {
  await page.goto(`${BASE_URL}/contracts`);
  await sleep(3000);

  // 使用多种选择器尝试获取合同ID
  const contracts = await page.evaluate(() => {
    const ids = [];

    // 方法1: 查找所有链接
    document.querySelectorAll('a').forEach(link => {
      const href = link.getAttribute('href') || '';
      const match = href.match(/\/contracts\/([^/]+)/);
      if (match && !ids.includes(match[1])) {
        ids.push(match[1]);
      }
    });

    // 方法2: 如果方法1没找到，尝试从表格行获取
    if (ids.length === 0) {
      document.querySelectorAll('tr').forEach(row => {
        const text = row.textContent || '';
        const match = text.match(/(ZH02-\d+|SGSC[A-Z]+\d+)/);
        if (match && !ids.includes(match[1])) {
          ids.push(match[1]);
        }
      });
    }

    return ids;
  });

  return contracts;
}

// 验证仪表盘
async function verifyDashboard(page) {
  log('验证仪表盘...');
  const result = { page: '仪表盘', checks: [], passed: 0, failed: 0 };

  await page.goto(`${BASE_URL}/dashboard/overview`);
  await sleep(3000);

  // 检查KPI卡片
  const kpiCards = await page.$$('.bg-white');
  if (kpiCards.length >= 4) {
    result.checks.push({ name: 'KPI卡片数量', status: 'passed', value: kpiCards.length });
    result.passed++;
  } else {
    result.checks.push({ name: 'KPI卡片数量', status: 'failed', value: kpiCards.length });
    result.failed++;
  }

  // 检查是否有图表
  const charts = await page.$$('canvas, [class*="echarts"]');
  if (charts.length >= 1) {
    result.checks.push({ name: '图表渲染', status: 'passed', value: charts.length });
    result.passed++;
  } else {
    result.checks.push({ name: '图表渲染', status: 'warning', value: 0 });
    result.failed++;
    results.warnings.push('仪表盘图表可能未正确渲染');
  }

  // 截图
  await page.screenshot({ path: path.join(REPORT_DIR, '01-dashboard.png'), fullPage: true });
  result.screenshot = '01-dashboard.png';

  results.pages.push(result);
  log(`仪表盘验证完成: ${result.passed}/${result.checks.length} 通过`);
  return result;
}

// 验证合同列表
async function verifyContractList(page) {
  log('验证合同列表...');
  const result = { page: '合同列表', checks: [], passed: 0, failed: 0 };

  await page.goto(`${BASE_URL}/contracts`);
  await sleep(2000);

  // 检查表格
  const table = await page.$('table, .ant-table, [class*="vxe-table"]');
  if (table) {
    result.checks.push({ name: '合同表格存在', status: 'passed' });
    result.passed++;
  } else {
    result.checks.push({ name: '合同表格存在', status: 'failed' });
    result.failed++;
  }

  // 检查合同数量
  const rows = await page.$$('tr');
  const dataRows = rows.length - 1; // 减去表头
  result.checks.push({ name: '合同数据行数', status: 'passed', value: dataRows });
  result.passed++;

  // 截图
  await page.screenshot({ path: path.join(REPORT_DIR, '02-contracts-list.png'), fullPage: true });
  result.screenshot = '02-contracts-list.png';

  results.pages.push(result);
  log(`合同列表验证完成: ${result.passed}/${result.checks.length} 通过`);
  return result;
}

// 验证单个合同详情
async function verifyContractDetail(page, contractId) {
  const result = { contractId, checks: [], passed: 0, failed: 0, warnings: 0 };

  try {
    await page.goto(`${BASE_URL}/contracts/${contractId}`);
    await sleep(3000);

    // 检查页面标题
    const title = await page.$('h2, .text-xl');
    if (title) {
      result.checks.push({ name: '页面标题', status: 'passed' });
      result.passed++;
    } else {
      result.checks.push({ name: '页面标题', status: 'failed' });
      result.failed++;
    }

    // 检查KPI区域
    const kpiCards = await page.$$('.bg-white.rounded-lg');
    if (kpiCards.length >= 3) {
      result.checks.push({ name: 'KPI区域', status: 'passed', value: kpiCards.length });
      result.passed++;
    } else {
      result.checks.push({ name: 'KPI区域', status: 'warning', value: kpiCards.length });
      result.warnings++;
    }

    // 检查基本信息卡片
    const infoCards = await page.$$('.ant-card, [class*="card"]');
    if (infoCards.length >= 2) {
      result.checks.push({ name: '信息卡片', status: 'passed', value: infoCards.length });
      result.passed++;
    } else {
      result.checks.push({ name: '信息卡片', status: 'failed', value: infoCards.length });
      result.failed++;
    }

    // 检查是否有甘特图（科研类）
    const gantt = await page.$('canvas');
    if (gantt) {
      result.checks.push({ name: '甘特图渲染', status: 'passed' });
      result.passed++;
    }

    // 检查阶段表格
    const stageTable = await page.$('table');
    if (stageTable) {
      const stageRows = await page.$$('table tbody tr');
      if (stageRows.length > 0) {
        result.checks.push({ name: '阶段数据', status: 'passed', value: stageRows.length });
        result.passed++;
      } else {
        result.checks.push({ name: '阶段数据', status: 'warning', value: 0 });
        result.warnings++;
      }
    }

    // 检查付款进度
    const paymentCards = await page.$$('[class*="payment"], [class*="付款"]');
    if (paymentCards.length > 0) {
      result.checks.push({ name: '付款进度显示', status: 'passed' });
      result.passed++;
    }

    // 检查是否有错误提示
    const errorMsg = await page.$('.ant-message-error, .error-message');
    if (errorMsg) {
      result.checks.push({ name: '页面错误', status: 'failed' });
      result.failed++;
      const errorText = await errorMsg.textContent();
      result.errors = result.errors || [];
      result.errors.push(errorText);
    }

    // 截图
    const screenshotName = `contract-${contractId}.png`;
    await page.screenshot({ path: path.join(REPORT_DIR, screenshotName), fullPage: true });
    result.screenshot = screenshotName;

  } catch (error) {
    result.checks.push({ name: '页面加载', status: 'failed', error: error.message });
    result.failed++;
  }

  results.contracts.push(result);
  return result;
}

// 验证项目列表
async function verifyProjectList(page) {
  log('验证项目列表...');
  const result = { page: '项目列表', checks: [], passed: 0, failed: 0 };

  await page.goto(`${BASE_URL}/projects`);
  await sleep(2000);

  const table = await page.$('table, .ant-table');
  if (table) {
    result.checks.push({ name: '项目表格', status: 'passed' });
    result.passed++;
  } else {
    result.checks.push({ name: '项目表格', status: 'failed' });
    result.failed++;
  }

  await page.screenshot({ path: path.join(REPORT_DIR, '03-projects-list.png'), fullPage: true });
  result.screenshot = '03-projects-list.png';

  results.pages.push(result);
  return result;
}

// 验证发票列表
async function verifyInvoiceList(page) {
  log('验证发票列表...');
  const result = { page: '发票列表', checks: [], passed: 0, failed: 0 };

  await page.goto(`${BASE_URL}/invoices`);
  await sleep(2000);

  const table = await page.$('table, .ant-table');
  if (table) {
    result.checks.push({ name: '发票表格', status: 'passed' });
    result.passed++;
  } else {
    result.checks.push({ name: '发票表格', status: 'failed' });
    result.failed++;
  }

  await page.screenshot({ path: path.join(REPORT_DIR, '04-invoices-list.png'), fullPage: true });
  result.screenshot = '04-invoices-list.png';

  results.pages.push(result);
  return result;
}

// 验证供应商列表
async function verifySupplierList(page) {
  log('验证供应商列表...');
  const result = { page: '供应商列表', checks: [], passed: 0, failed: 0 };

  await page.goto(`${BASE_URL}/suppliers`);
  await sleep(2000);

  const table = await page.$('table, .ant-table');
  if (table) {
    result.checks.push({ name: '供应商表格', status: 'passed' });
    result.passed++;
  } else {
    result.checks.push({ name: '供应商表格', status: 'failed' });
    result.failed++;
  }

  await page.screenshot({ path: path.join(REPORT_DIR, '05-suppliers-list.png'), fullPage: true });
  result.screenshot = '05-suppliers-list.png';

  results.pages.push(result);
  return result;
}

// 主验证流程
async function main() {
  console.log('='.repeat(60));
  console.log('开始全面系统验证');
  console.log('='.repeat(60));

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  // 收集控制台错误
  page.on('console', msg => {
    if (msg.type() === 'error') {
      results.errors.push({ page: page.url(), message: msg.text() });
    }
  });

  try {
    // 1. 登录
    log('访问系统...');
    await page.goto(BASE_URL);
    await sleep(2000);

    // 检查是否需要登录
    if (page.url().includes('login')) {
      log('执行登录...');
      // 等待登录表单加载
      await sleep(1000);

      // 查找用户名和密码输入框
      const inputs = await page.$$('input');
      if (inputs.length >= 2) {
        // 填写用户名
        await inputs[0].fill('admin');
        await sleep(500);
        // 填写密码
        await inputs[1].fill('admin123');
        await sleep(500);
      }

      // 点击登录按钮
      const loginBtn = await page.$('button[type="submit"], button:has-text("登录"), button:has-text("登")');
      if (loginBtn) {
        await loginBtn.click();
      } else {
        // 尝试按回车
        await page.keyboard.press('Enter');
      }
      await sleep(3000);
    }

    // 2. 验证主要页面
    await verifyDashboard(page);
    await verifyContractList(page);
    await verifyProjectList(page);
    await verifyInvoiceList(page);
    await verifySupplierList(page);

    // 3. 获取所有合同并逐一验证
    log('获取所有合同ID...');
    const contracts = await getAllContracts(page);
    log(`发现 ${contracts.length} 个合同`);

    // 验证每个合同详情
    let count = 0;
    for (const contractId of contracts) {
      count++;
      log(`验证合同 [${count}/${contracts.length}]: ${contractId}`);
      await verifyContractDetail(page, contractId);

      // 每10个合同输出一次进度
      if (count % 10 === 0) {
        const passed = results.contracts.filter(c => c.failed === 0).length;
        log(`进度: ${count}/${contracts.length}, 成功: ${passed}`);
      }
    }

    // 4. 统计结果
    results.endTime = new Date().toISOString();
    results.summary.total = results.pages.length + results.contracts.length;
    results.summary.passed = [...results.pages, ...results.contracts].filter(r => r.failed === 0).length;
    results.summary.failed = [...results.pages, ...results.contracts].filter(r => r.failed > 0).length;
    results.summary.warnings = [...results.pages, ...results.contracts].reduce((sum, r) => sum + (r.warnings || 0), 0);

    // 5. 生成报告
    const reportPath = path.join(REPORT_DIR, 'verification-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));

    // 6. 输出摘要
    console.log('\n' + '='.repeat(60));
    console.log('验证完成！');
    console.log('='.repeat(60));
    console.log(`总体验证: ${results.summary.passed}/${results.summary.total} 通过`);
    console.log(`页面验证: ${results.pages.filter(p => p.failed === 0).length}/${results.pages.length} 通过`);
    console.log(`合同验证: ${results.contracts.filter(c => c.failed === 0).length}/${results.contracts.length} 通过`);
    console.log(`警告数量: ${results.summary.warnings}`);
    console.log(`错误数量: ${results.errors.length}`);
    console.log(`\n报告已保存: ${reportPath}`);
    console.log(`截图目录: ${REPORT_DIR}`);

    // 列出失败的合同
    const failedContracts = results.contracts.filter(c => c.failed > 0);
    if (failedContracts.length > 0) {
      console.log('\n失败合同列表:');
      failedContracts.forEach(c => {
        console.log(`  - ${c.contractId}: ${c.failed} 项失败`);
      });
    }

  } catch (error) {
    console.error('验证过程出错:', error.message);
    results.errors.push({ fatal: true, message: error.message });
  } finally {
    await browser.close();
  }
}

main();
