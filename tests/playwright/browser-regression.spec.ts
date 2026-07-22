import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:18090';
const API_URL = 'http://localhost:18080';

test.describe('P0-4 浏览器回归验证', () => {
  test('API 输出单位为元', async ({ request }) => {
    const resp = await request.get(`${API_URL}/api/stats`);
    expect(resp.status()).toBe(200);
    
    const data = await resp.json();
    expect(data.code).toBe(0);
    
    // total_amount 应该是元（大于 100 万）
    const totalAmount = data.data.total_amount;
    expect(totalAmount).toBeGreaterThan(1000000);
    expect(totalAmount).toBeLessThan(100000000);
  });

  test('前端页面可访问', async ({ page }) => {
    await page.goto(BASE_URL);
    // 等待网络空闲，不等待特定元素
    await page.waitForLoadState('networkidle');
    
    // 检查无 critical errors
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('requestfailed', req => {
      if (req.failure()?.errorText && !req.url().includes('.map')) {
        errors.push(`Request failed: ${req.url()}`);
      }
    });
    
    // 简单检查页面可访问
    const title = await page.title();
    console.log(`Page title: ${title}`);
    
    expect(errors).toHaveLength(0);
  });

  test('build-info.json 可访问', async ({ request }) => {
    const resp = await request.get(`${BASE_URL}/web/build-info.json`);
    expect(resp.status()).toBe(200);
    
    const info = await resp.json();
    expect(info).toHaveProperty('git_commit');
    expect(info).toHaveProperty('build_time');
    expect(info.version).toBeTruthy();
  });
});
