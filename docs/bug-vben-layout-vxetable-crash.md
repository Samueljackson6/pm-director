# Bug Report: Vben Admin BasicLayout 在自定义路由上触发 VxeTable 渲染崩溃

**报告日期**: 2026-07-08
**发现阶段**: P2 T9 前端财务仪表盘接入验证

---

## 问题描述

在 Vben Admin 5 中添加一个独立路由（非 `/dashboard` 子路由），指向 `views/dashboard/index.vue` 时，BasicLayout 在渲染过程中抛出 `TypeError: Cannot destructure property 'row' of 'undefined'` 错误，导致整个页面白屏（仅渲染出侧边栏外壳，主内容区域为空）。

该错误来自 Vben Admin 运行时 bundle（`js/index-*.js`）中的 VxeTable 相关代码，非业务组件代码。

## 复现步骤

1. 在 `src/router/routes/modules/` 中添加一个路由配置，例如：

```typescript
routes.push({
  name: 'FinanceDashboardParent',
  path: '/finance-dashboard',
  component: () => import('#/layouts/basic.vue'),
  meta: { icon: 'lucide:bar-chart', title: '财务仪表盘', ignoreAccess: true },
  children: [{
    name: 'FinanceDashboard',
    path: '',
    component: () => import('#/views/dashboard/index.vue'),
    meta: { title: '财务仪表盘', ignoreAccess: true }
  }]
});
```

2. 登录后通过 SPA 路由导航到 `/finance-dashboard`（`router.push('/finance-dashboard')` 或直接 `page.goto('/web/finance-dashboard')`）
3. 页面 URL 正确，但主内容区空白

## 实际行为

- URL 正确解析为 `/finance-dashboard`
- 浏览器控制台输出错误：
  ```
  TypeError: Cannot destructure property 'row' of 'undefined' as it is undefined.
      at http://localhost:8900/web/js/index-*.js:1:4879
      at r (http://localhost:8900/web/jse/index-index-*.js:14:32607)
      at os (http://localhost:8900/web/jse/index-index-*.js:16:42892)
      at ca (http://localhost:8900/web/jse/index-index-*.js:16:40990)
      at pd (http://localhost:8900/web/jse/index-index-*.js:16:41517)
  ```
- 页面 body 仅渲染侧边栏和头部（约 56 字符），无主内容
- `bodyLen=56`，只包含侧边栏菜单文字

## 期望行为

页面正常渲染业务组件内容，BasicLayout 不应在自定义路由上抛出未捕获的渲染异常。

## 定位分析

### 确认的事实

1. **错误来自 Vben Admin 运行时 bundle**（`js/index-*.js` 和 `jse/index-index-*.js`），不是业务组件代码
2. **同个 BasicLayout 在其他路由上正常渲染**：`/contracts/list`、`/invoices/list`、`/suppliers/list` 均正常显示内容（40/50/24 行数据）
3. **仅在通过独立路由（非 `/dashboard` 子路由）访问时触发**：`/dashboard/overview`（原 `/dashboard` 子路由）也被 Vben 的 `@vben/access` 在运行时删除了自定义子路由
4. **0 业务控制台错误**：除该 VxeTable 布局错误外，无其他 JS 异常

### 疑似根因

Vben Admin 的 `@vben/access` 模块中的 `generateAccessible()` 函数对路由进行了运行时处理。当检测到路由不匹配其预期的可访问菜单结构时，BasicLayout 可能触发了一个内置的 VxeTable 渲染逻辑，该逻辑假设 `row` 数据存在但未做空值保护。

具体来说：
- Vben 对 `/dashboard` 父路由有内置处理（自动注入 analytics 子页）
- 当自定义路由使用 `basic.vue` 布局且路径独立于 `/dashboard` 时，布局尝试渲染一个 VxeTable 组件（可能是全局组件或 layout 级别的 VxeTable）
- 该 VxeTable 的 template slot `{ row }` 在数据未定义时直接解构导致崩溃

## 影响范围

- 任何通过独立顶级路由（非 `/dashboard` 子路由）添加的新页面都可能触发此问题
- 通过 `/dashboard/*` 子路由添加的页面（如 `analytics`）不受影响（但自定义子路由会被 Vben 自动清理）
- 受影响的业务功能：财务仪表盘页面

## 临时规避

财务仪表盘可通过 `@vben/access` 的菜单配置系统注册，或使用 `/dashboard` 父路由的默认子路由机制（需进一步研究 Vben 的 access 路由处理逻辑）。

## 环境

- Vben Admin 5.6.0
- Vite 7.3.6
- Vue 3.5.39
- Playwright 1.61.1（用于复现）
- 本地 Docker 环境（backend 8800, frontend nginx 8900/web/）

## 后续建议

1. 检查 `@vben/access` 的 `generateAccessible()` 源码，理解其对独立路由的处理逻辑
2. 在 BasicLayout 的 VxeTable 渲染处添加空值保护
3. 或改用 Vben 标准的菜单注册方式（通过后端菜单 API + accessStore 注册）
