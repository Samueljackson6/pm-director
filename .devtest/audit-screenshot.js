const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:18090/web';
const AUDIT_DIR = path.join(__dirname, 'audit-screenshots');

// 确保输出目录存在
if (!fs.existsSync(AUDIT_DIR)) {
  fs.mkdirSync(AUDIT_DIR, { recursive: true });
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  console.log('启动浏览器...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();

  try {
    // 1. 登录页
    console.log('1. 访问登录页...');
    await page.goto(`${BASE_URL}/dashboard/overview`);
    await sleep(2000);

    // 检查是否需要登录
    const currentUrl = page.url();
    if (currentUrl.includes('login')) {
      console.log('需要登录，执行登录操作...');
      // 点击登录按钮
      await page.click('button:has-text("登")');
      await sleep(3000);
    }

    // 2. 仪表盘首页
    console.log('2. 截取仪表盘...');
    await page.goto(`${BASE_URL}/dashboard/overview`);
    await sleep(2000);
    await page.screenshot({
      path: path.join(AUDIT_DIR, '01-dashboard.png'),
      fullPage: true
    });
    console.log('   保存: 01-dashboard.png');

    // 3. 合同列表
    console.log('3. 截取合同列表...');
    await page.goto(`${BASE_URL}/contracts`);
    await sleep(2000);
    await page.screenshot({
      path: path.join(AUDIT_DIR, '02-contracts-list.png'),
      fullPage: true
    });
    console.log('   保存: 02-contracts-list.png');

    // 4. 科研类合同详情 - ZH02-202408007
    console.log('4. 截取科研类合同详情 (ZH02-202408007)...');
    await page.goto(`${BASE_URL}/contracts/ZH02-202408007`);
    await sleep(3000);
    await page.screenshot({
      path: path.join(AUDIT_DIR, '03-research-detail-1.png'),
      fullPage: true
    });
    console.log('   保存: 03-research-detail-1.png');

    // 5. 科研类合同详情 - ZH02-202604023
    console.log('5. 截取科研类合同详情 (ZH02-202604023)...');
    await page.goto(`${BASE_URL}/contracts/ZH02-202604023`);
    await sleep(3000);
    await page.screenshot({
      path: path.join(AUDIT_DIR, '04-research-detail-2.png'),
      fullPage: true
    });
    console.log('   保存: 04-research-detail-2.png');

    // 6. 服务类合同详情 - ZH02-202601005
    console.log('6. 截取服务类合同详情 (ZH02-202601005)...');
    await page.goto(`${BASE_URL}/contracts/ZH02-202601005`);
    await sleep(3000);
    await page.screenshot({
      path: path.join(AUDIT_DIR, '05-service-detail-1.png'),
      fullPage: true
    });
    console.log('   保存: 05-service-detail-1.png');

    // 7. 项目列表
    console.log('7. 截取项目列表...');
    await page.goto(`${BASE_URL}/projects`);
    await sleep(2000);
    await page.screenshot({
      path: path.join(AUDIT_DIR, '06-projects-list.png'),
      fullPage: true
    });
    console.log('   保存: 06-projects-list.png');

    // 8. 控制台错误检查
    console.log('8. 检查控制台错误...');
    const consoleLogs = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleLogs.push(msg.text());
      }
    });

    // 重新访问页面收集错误
    await page.goto(`${BASE_URL}/contracts/ZH02-202408007`);
    await sleep(3000);

    // 保存控制台错误
    const errorReport = {
      timestamp: new Date().toISOString(),
      consoleErrors: consoleLogs
    };
    fs.writeFileSync(
      path.join(AUDIT_DIR, 'console-errors.json'),
      JSON.stringify(errorReport, null, 2)
    );
    console.log(`   发现 ${consoleLogs.length} 个控制台错误`);

    console.log('\n=== 审计完成 ===');
    console.log(`截图保存至: ${AUDIT_DIR}`);

  } catch (error) {
    console.error('审计失败:', error.message);
  } finally {
    await browser.close();
  }
}

main();
