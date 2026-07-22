import { test, expect } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || 'http://localhost:18090/web/'

test.describe('P0 浏览器截图验证', () => {
  test('dashboard 首页可访问 + 截图', async ({ page }) => {
    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(3000)
    const screenshot = await page.screenshot({ fullPage: true })
    await expect(screenshot).toBeTruthy()
    // 保存截图到 test-results/p0-screenshots/
    const fs = require('fs')
    const dir = 'test-results/p0-screenshots'
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
    fs.writeFileSync(`${dir}/01-dashboard.png`, screenshot)
    console.log('✅ dashboard 截图已保存: test-results/p0-screenshots/01-dashboard.png')
  })

  test('登录页可访问 + 截图', async ({ page }) => {
    await page.goto(BASE_URL + 'auth/login')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)
    const screenshot = await page.screenshot({ fullPage: true })
    await expect(screenshot).toBeTruthy()
    const fs = require('fs')
    const dir = 'test-results/p0-screenshots'
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
    fs.writeFileSync(`${dir}/02-login.png`, screenshot)
    console.log('✅ login 截图已保存: test-results/p0-screenshots/02-login.png')
  })

  test('API /api/stats 返回元单位', async ({ request }) => {
    const resp = await request.get('http://localhost:18080/api/stats')
    const data = await resp.json()
    const total = data.data?.total_amount ?? data.total_amount
    console.log(`total_amount = ${total} (应为 > 1000000，即万元级转元)`)
    expect(total).toBeGreaterThan(1000000)
  })

  test('build-info.json 可访问', async ({ request }) => {
    const resp = await request.get(BASE_URL + 'build-info.json')
    expect(resp.status()).toBe(200)
    const body = await resp.json()
    console.log(`build-info: git_commit=${body.git_commit?.substring(0,7)}, version=${body.version}`)
    expect(body.version).toBeTruthy()
  })
})
