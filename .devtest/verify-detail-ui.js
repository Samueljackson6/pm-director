/**
 * 验证合同详情页 UI 渲染
 */
import { chromium } from 'playwright';

const BASE_URL = 'http://localhost:8900';

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  // 登录
  console.log('登录...');
  await page.goto(`${BASE_URL}/web/auth/login`, { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(1000);
  const inputs = await page.locator('input').all();
  if (inputs.length >= 2) {
    await inputs[0].fill('admin');
    await inputs[1].fill('admin123');
  }
  await page.locator('button[type="submit"]').click();
  await page.waitForTimeout(2000);
  console.log('登录成功:', page.url());

  // 导航到合同详情
  console.log('导航到合同详情...');
  await page.goto(`${BASE_URL}/web/contracts/detail?id=SGSCCD00CYJS240162`, { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(5000);
  console.log('当前URL:', page.url());

  const bodyText = await page.textContent('body');
  console.log('页面文字检测:');
  console.log('  合同金额:', bodyText.includes('合同金额'));
  console.log('  税率:', bodyText.includes('税率'));
  console.log('  SGSC:', bodyText.includes('SGSC'));
  console.log('  付款进度:', bodyText.includes('付款进度'));
  console.log('  阶段进度:', bodyText.includes('阶段进度'));
  console.log('  违约:', bodyText.includes('违约'));

  const stats = await page.locator('.ant-statistic').count();
  console.log('a-statistic 数量:', stats);

  const progress = await page.locator('.ant-progress').count();
  console.log('a-progress 数量:', progress);

  const cards = await page.locator('.ant-card').count();
  console.log('ant-card 数量:', cards);

  await page.screenshot({ path: '.devtest/verify-final-2.png', fullPage: true });
  console.log('截图保存成功');

  await browser.close();
}

main().catch(err => {
  console.error('错误:', err.message);
  process.exit(1);
});
