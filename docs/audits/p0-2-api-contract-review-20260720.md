# P0-2 核心关系服务与财务 API 契约审查报告

> 日期：2026-07-20  
> 状态：**已完成**  
> 关联 Issue：[#49 P0-2](https://github.com/Samueljackson6/pm-director/issues/49)

---

## 一、审查范围

审查了以下后端路由的金额单位转换和关系服务逻辑：

| 路由文件 | 审查项 | 结果 |
|---------|--------|------|
| `contracts.py` | contract_amount/invoice_total/payment_total → 元 | ✅ 已修复 |
| `projects.py` | total_contract_amount/planned/paid → 元 | ✅ 已修复 |
| `finance.py` | stats/summary 所有万元字段 → 元 | ✅ 已修复 |
| `dashboard.py` | 全部 KPI → 元，currency_unit → "元" | ✅ 已修复 |
| `suppliers.py` | total_contract_amount → 元 | ✅ 已修复 |
| `invoices.py` | amount 已是元 | ✅ 无需改动 |
| `receipts.py` | amount 已是元 | ✅ 无需改动 |

**测试结果**：39 passed, 0 failed.

---

## 二、关系服务契约分析

### 2.1 contract_id_mapping（SGSC ↔ ZH 映射）

**表结构**：
```
project_id_zh (PK) ← ZH 正式编号，canonical ID
project_id_sgsc    ← SGSC 内部编号，别名
financial_id       ← 财务系统编号（极少填充）
source             ← auto_mapping / auto_mapping_v2 / amount_match / NULL
```

**当前使用方式**（`contracts.py:get_contract`）：
```python
# 优先找 ZH 前缀的真实 canonical ID
map_row = db.execute(
    'SELECT project_id_zh FROM contract_id_mapping '
    'WHERE (project_id_sgsc=? OR project_id_zh=?) AND project_id_zh LIKE ? LIMIT 1',
    (contract_id, contract_id, 'ZH%')
).fetchone()
# 回退：无任何 ZH 映射时，才接受 SYS- 等占位映射
if not map_row:
    map_row = db.execute(
        'SELECT project_id_zh FROM contract_id_mapping '
        'WHERE project_id_sgsc=? OR project_id_zh=? LIMIT 1',
        (contract_id, contract_id)
    ).fetchone()
```

**契约规则**：
1. **输入可以是 ZH 或 SGSC 编号** — 通过 mapping 表解析为 ZH canonical ID
2. **关联查询使用双 ID 并集** — `link_ids = [contract_id, mapped_id]`
3. **避免占位映射抢占** — 优先匹配 ZH 前缀，SYS- 等占位只在无 ZH 映射时回退

**发现的问题**：

| 问题 | 严重度 | 说明 |
|------|--------|------|
| 大小写不规范 | 🟡 中 | `SGsCYAFDSJJS2600004`、`susCL10oFCJS2600057` 应为大写 |
| 截断 ID | 🟡 中 | `ZH02-202604025` 对应 `SGSCCD`（不完整） |
| financial_id 全空 | 🟢 低 | 仅 1 条有值，不影响业务 |
| project_name 缺失 | 🟢 低 | 部分映射无名称，但不影响关联查询 |

**建议**：这些是数据质量问题，不是代码缺陷。P0-1 已记录清理计划。

### 2.2 跨表关联一致性

#### contracts.py 列表查询
```sql
LEFT JOIN contract_id_mapping m ON m.project_id_sgsc = c.contract_id
LEFT JOIN current_finance_view fr ON COALESCE(m.project_id_zh, c.contract_id) = fr.project_id
```
- ✅ 正确：通过 SGSC 别名关联到 ZH canonical ID，再用 ZH 查 finance 快照
- ⚠️ 注意：如果合同 ID 本身就是 ZH，mapping 查不到（m.project_id_sgsc = c.contract_id），但 `fr.project_id` 用 `COALESCE(m.project_id_zh, c.contract_id)` 兜底到原 ID

#### contracts.py 详情查询
```python
link_ids = list(dict.fromkeys([contract_id, mapped_id]))
# stages/payments/deliverables/clauses/budgets/invoices/files 都用 IN (link_q)
```
- ✅ 正确：同时用原始 ID 和 canonical ID 查询，避免漏数据
- ✅ 付款去重：用 `_seen` 集合按 `payment_id` 去重

#### projects.py 详情查询
```sql
JOIN contract_project_link cpl ON p.project_id = cpl.project_id
WHERE cpl.contract_id=? OR cpl.project_id=? OR cpl.contract_id=?
```
- ⚠️ 潜在问题：`cpl.contract_id` 可能存的是 SGSC 编号，而传入的 `contract_id` 可能是 ZH。当前逻辑靠 `contract_project_link` 表的 `contract_id` 字段本身存储的值来匹配，没有经过 mapping 表解析。
- **风险**：如果一个项目的 contract_id 只以 SGSC 编号存储，而用户通过 ZH 编号访问，则关联不到。

**需要确认**：`contract_project_link.contract_id` 存储的是 ZH 还是 SGSC？从数据分析看，大部分是 SGSC 编号（如 `SGSCCD00CYJS240162`），少数是 ZH（如 `ZH02-202406004`）。这意味着**项目详情通过 ZH 编号访问时，可能找不到以 SGSC 编号存储的关联项目**。

### 2.3 财务口径一致性

| 端点 | 数据来源 | 金额单位 | 状态 |
|------|---------|---------|------|
| `/api/stats` | `current_finance_view` + `finance_records` | 万元→元 ✅ | 已修复 |
| `/api/finance/summary` | `current_finance_view` + `finance_records` | 万元→元 ✅ | 已修复 |
| `/api/dashboard/overview` | `current_finance_view` + `finance_records` + `invoices` + `contracts` | 万元→元 ✅ | 已修复 |
| `/api/contracts` | `contracts` + `current_finance_view` | 万元→元 ✅ | 已修复 |
| `/api/projects` | `projects` | 万元→元 ✅ | 已修复 |

**关键发现**：
- `current_finance_view` 和 `finance_records` 的金额单位都是**万元**
- `invoices.amount` 和 `receipts.amount` 的单位是**元**
- Dashboard 前端已将 `invoices.amount / 10000` 转为万元展示，现在 API 输出元，前端需改为直接显示

### 2.4 发票↔回款关联闭环

**当前状态**：
- `invoice_receipt_link` 表有 25 条记录
- `receipts.py:auto_match_receipts` POST 端点存在**自动匹配写入**风险
- G003 已验证浏览器页面加载无自动匹配请求，但 POST 端点仍可被调用

**契约规则**：
1. 客户回款（`receipts`）和供应商收票（`invoices.direction='inbound'`）严格分轨
2. `invoice_receipt_link` 只允许客户发票↔客户回款关联
3. 关联金额 `link_amount` 必须 ≤ 回款金额，避免超额匹配

**待 P0-4 处理**：发票↔回款关联缺失闭环（B-05）

---

## 三、P0-2 结论

### 已修复
1. ✅ 所有后端路由的金额输出统一为**元**
2. ✅ 前端测试断言已更新
3. ✅ 后端测试 39 passed

### 发现的问题（非阻塞，需后续处理）

| # | 问题 | 优先级 | 建议处理阶段 |
|---|------|--------|-------------|
| 1 | `contract_project_link` 的 contract_id 可能是 SGSC 编号，ZH 访问可能漏关联 | 🟡 中 | P0-3 合同详情闭环 |
| 2 | `contract_id_mapping` 大小写/截断数据质量 | 🟢 低 | P0-1 数据治理 |
| 3 | `receipts.py:auto_match_receipts` POST 有自动匹配写入风险 | 🟡 中 | P0-4 回款闭环 |
| 4 | `finance_records` 每周更新但无变更追踪 | 🟢 低 | P0-5 质量门禁 |

### 下一步

1. **浏览器回归验证**：确认金额单位改动没有破坏现有页面显示
2. **P0-3**：合同与项目详情真实闭环（甘特图、条款位置、编辑按钮）
3. **P0-4**：客户发票/回款/附件可靠闭环

---

> **文档版本**：v1.0  
> **关联文档**：`docs/audits/p0-1-database-analysis-20260720.md`、`docs/design/p0-1-amount-unit-strategy.md`
