# P0-4 前端金额组件改造 + Playwright 回归验证报告

> 日期：2026-07-21  
> 状态：**前端改造完成，Playwright 待执行**

---

## 一、前端金额组件改造 ✅

### 改造范围

| 文件 | 改动 |
|------|------|
| `ui/src/utils/formatAmount.ts` | 新建统一格式化工具函数 |
| `ui/src/views/dashboard/index.vue` | 统计卡片 + 最近合同表格 → formatWanYuan |
| `ui/src/views/contracts/index.vue` | 合同列表 3 个金额列 → formatWanYuan |
| `ui/src/views/contracts/detail.vue` | 合同金额 + 付款计划 → formatWanYuan |
| `ui/src/views/projects/index.vue` | 项目列表合同总额列 → formatWanYuan |
| `ui/src/views/projects/detail.vue` | 项目总金额 + 关联合同 + 付款时间线 → formatWanYuan |
| `ui/src/views/invoices/index.vue` | 财务汇总卡片 + 发票/税额列 → formatWanYuan |
| `ui/src/views/suppliers/index.vue` | 供应商列表 4 个金额列 → formatWanYuan |

### 使用方式

```typescript
import { formatWanYuan } from '@/utils/formatAmount'

// 模板中使用
{{ formatWanYuan(row.contract_amount) }}

// JS 中使用
const wanValue = formatWanYuan(1250850) // => "125.09"
```

### 验证结果

所有 7 个页面文件均包含：
- ✅ `formatWanYuan` 导入
- ✅ `@/utils/formatAmount` 引用
- ✅ 金额展示使用 `formatWanYuan` 替代 `.toFixed(2)`

---

## 二、Playwright 浏览器回归验证（待执行）

### 测试计划

基于 Codex 审计报告的任务流，编写 Playwright 脚本验证：

1. **登录流程** — 访问系统并登录
2. **经营工作台** — 验证 KPI 卡片金额显示正确（万元展示）
3. **合同台账** — 验证列表金额列显示正确
4. **合同详情** — 验证详情页金额显示正确
5. **项目台账** — 验证列表金额列显示正确
6. **客户发票** — 验证发票金额显示正确
7. **供应商** — 验证供应商金额显示正确
8. **四视口检查** — 1440/1024/768/390 布局无异常
9. **数据库零变更** — SHA256 前后一致

### 待编写脚本

- `tests/playwright/browser-regression.spec.ts`
- `tests/playwright/fixtures/login.ts`

### 前置条件

- [ ] Docker 构建成功（当前网络超时，需手动 build）
- [ ] 前端代码编译通过
- [ ] 浏览器可访问 http://localhost:18090

---

## 三、下一步

1. 解决 Docker 构建网络问题
2. 编写 Playwright 回归脚本
3. 执行浏览器回归验证
4. 清理临时脚本

---

> **文档版本**：v1.0  
> **下次更新**：Playwright 脚本完成后
