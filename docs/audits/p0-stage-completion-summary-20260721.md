# P0 阶段完成总结报告

> 日期：2026-07-21  
> 状态：**已完成**

---

## 一、P0-0 ✅ 运行基线、备份与发布可追溯

| 改动 | 文件 |
|------|------|
| `get_db()` 移除 `_init_tables()` 自动建表 | `backend/database.py` |
| 新建迁移脚本供首次部署/表结构变更时显式执行 | `backend/scripts/migrate.py` |
| 构建产物指纹生成脚本 | `scripts/generate-build-info.py` |
| 后端测试 | 39 passed ✅ |

**关键发现**：接管基线 SHA256 与当前运行态不一致，原因是 `get_db()` 每次连接自动创建 `supplier_contacts` 表。已修复。

---

## 二、P0-1 ✅ 数据真值、金额单位与关系契约

### 核心结论

| 发现 | 结论 |
|------|------|
| 金额单位混用 | `contracts`/`payments`/`finance_records` = **万元**；`invoices`/`receipts`/`master_table` = **元** |
| 主数据源 | `contracts` → `projects` → `suppliers`（主档），`invoices`/`receipts`/`payments`（交易流水） |
| 财务快照 | `finance_records`/`current_finance_view`/`master_table` 为 Excel 导入的历史快照，应降级为只读参考 |
| contract_id_mapping | SGSC↔ZH 编号映射表，应以 ZH 编号为 canonical ID |
| master_table vs contracts | 比值精确 0.0001，确认 master_table 是原始元数据（元），contracts 是转换后的万元值 |

### 决策（用户确认）

1. 金额单位统一为**元** — DB 不动，API 输出元
2. contract_id_mapping — 以 ZH 编号为 canonical ID
3. finance_records / current_finance_view / master_table — 降级为只读参考，初期保持每周更新，后续演变为审计库

### 产出文档

- `docs/audits/p0-1-database-analysis-20260720.md` — 完整数据库分析
- `docs/design/p0-1-amount-unit-strategy.md` — 金额单位策略决策
- `docs/design/p0-1-historical-snapshot-downgrade.md` — 历史快照降级说明 + 审计库演化建议

---

## 三、P0-2 ✅ 核心关系服务与财务 API 契约

### 代码修改

| 路由 | 改动 |
|------|------|
| `contracts.py` | contract_amount/invoice_total/payment_total → ×10000 |
| `projects.py` | total_contract_amount/planned/paid → ×10000 |
| `finance.py` | stats/summary 所有万元字段 → ×10000 |
| `dashboard.py` | 全部 KPI → 元，currency_unit → "元" |
| `suppliers.py` | total_contract_amount → ×10000 |
| `test_dashboard.py` | 断言更新为期望"元" |
| `backend/utils/amount_converter.py` | 新增统一转换工具 |

### 关系服务审查发现（非阻塞）

| # | 问题 | 优先级 | 建议处理阶段 |
|---|------|--------|-------------|
| 1 | `contract_project_link.contract_id` 可能存 SGSC 编号，ZH 访问可能漏关联 | 🟡 中 | P0-3 合同详情闭环 |
| 2 | `contract_id_mapping` 大小写/截断数据质量 | 🟢 低 | P0-1 数据治理 |
| 3 | `receipts.py:auto_match_receipts` POST 有自动匹配写入风险 | 🟡 中 | P0-4 回款闭环 |
| 4 | `finance_records` 无变更追踪 | 🟢 低 | P0-5 质量门禁 |

### 验证结果

- 后端测试：39 passed ✅
- API 验证：`/api/stats` 返回 `total_amount=24564900.0`（原 2456.49 万元）✅

---

## 四、P0-4 ✅ 前端金额组件改造 + 浏览器回归验证

### 前端改动

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

### Playwright 回归验证

```bash
cd tests/playwright && npm install && npx playwright test
```

**结果**：3 passed ✅

| 测试 | 状态 |
|------|------|
| API 输出单位为元 | ✅ |
| 前端页面可访问 | ✅ |
| build-info.json 可访问 | ✅ |

---

## 五、待完成事项

### 5.1 P0-3 合同与项目详情真实闭环（待 P0-4 之后）

| 问题编号 | 内容 | 优先级 |
|---------|------|--------|
| B-03 | 甘特图空白（接口有数据但前端未渲染） | P0 |
| B-04 | 合同条款位置错误（应在页尾） | P0 |
| B-06 | 多处编辑/新增按钮为空白占位 | P0 |

### 5.2 P0-5 质量门禁、回归测试与受控发布

- CI 门禁
- 回归测试自动化
- Docker 镜像标签管理
- 发布流程规范化

### 5.3 P0-6 历史数据补录与持续数据质量机制

- 历史数据补录（需业务确认）
- 持续数据质量监控
- finance_records 变更追踪机制

---

## 六、交付物清单

### 代码文件

| 文件 | 类型 |
|------|------|
| `backend/database.py` | 修改 |
| `backend/scripts/migrate.py` | 新增 |
| `backend/utils/__init__.py` | 新增 |
| `backend/utils/amount_converter.py` | 新增 |
| `backend/routers/contracts.py` | 修改 |
| `backend/routers/projects.py` | 修改 |
| `backend/routers/finance.py` | 修改 |
| `backend/routers/dashboard.py` | 修改 |
| `backend/routers/suppliers.py` | 修改 |
| `backend/tests/test_dashboard.py` | 修改 |
| `ui/src/utils/formatAmount.ts` | 新增 |
| `ui/src/views/dashboard/index.vue` | 修改 |
| `ui/src/views/contracts/index.vue` | 修改 |
| `ui/src/views/contracts/detail.vue` | 修改 |
| `ui/src/views/projects/index.vue` | 修改 |
| `ui/src/views/projects/detail.vue` | 修改 |
| `ui/src/views/invoices/index.vue` | 修改 |
| `ui/src/views/suppliers/index.vue` | 修改 |
| `tests/playwright/browser-regression.spec.ts` | 新增 |
| `tests/playwright/playwright.config.ts` | 新增 |
| `scripts/generate-build-info.py` | 新增 |

### 文档

| 文件 | 内容 |
|------|------|
| `docs/audits/p0-1-database-analysis-20260720.md` | 完整数据库分析 |
| `docs/design/p0-1-amount-unit-strategy.md` | 金额单位策略决策 |
| `docs/design/p0-1-historical-snapshot-downgrade.md` | 历史快照降级说明 |
| `docs/audits/p0-2-api-contract-review-20260720.md` | 关系服务契约审查报告 |
| `docs/design/p0-4-task-spec-update-20260720.md` | P0-4 任务说明更新 |
| `docs/audits/p0-0-to-p0-2-progress-20260720.md` | 今日进度记录 |
| `docs/audits/p0-4-frontend-fix-report-20260721.md` | 前端改造报告 |
| `docs/audits/p0-stage-completion-summary-20260721.md` | P0 阶段完成总结 |

---

## 七、下一步行动

1. **P0-3**：合同与项目详情真实闭环（B-03/B-04/B-06）
2. **P0-4 业务闭环**：发票↔回款关联（B-05）、编辑/新增按钮（B-06）、附件上传（B-07）、供应商数据（B-08）
3. **P0-5**：质量门禁、回归测试与受控发布
4. **P0-6**：历史数据补录与持续数据质量机制

---

> **文档版本**：v1.0  
> **下次更新**：P0-3/P0-4 业务闭环完成后
