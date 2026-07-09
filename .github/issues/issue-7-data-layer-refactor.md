# Issue #7：数据层改造（ID格式统一 + OCR清洗 + 关联视图）

**优先级**：中（在前端 UI 重构完成后推进）  
**标签**：`data`, `backend`, `database`, `refactor`  
**创建时间**：2026-07-09  
**关联 Issue**：#4（合同详情页 UI 重构）、#5（发票/供应商详情修复）

---

## 📋 问题描述

当前数据库存在 **ID 格式混用** 和 **OCR 数据噪声** 问题，导致合同-项目-发票-供应商-收付款之间的关联断裂。

### 核心问题

1. **合同 ID 格式混用**：
   - `contracts` 表：`SGSC*` 和 `ZH02*` 两种格式并存
   - `invoices.project_id`：`ZH02*` 格式
   - `payments.contract_id`：部分 `SGSC*`，32 条无法匹配
   - `supplier_contracts.project_id`：`ZH02*` 格式
   - **结果**：发票/付款/供应商合同无法直接关联到合同

2. **OCR 数据噪声**：
   - `expiry_date` 字段被填入合同编号文本（如 `SGTYHT/25-JS-004 技术服务合同...`）
   - `sign_date` 仍有 15 份合同为 NULL
   - **结果**：日期字段无法用于业务逻辑

3. **关联视图错误**：
   - `current_finance_view` 用 `fr.project_id = c.contract_id` 关联，但格式不匹配
   - **结果**：财务汇总数据错误

---

## 🔧 改造方案

### Step 1：统一 ID 格式（关键）

**目标**：所有表使用统一的合同 ID 格式（`ZH02*`）

#### 1.1 确定唯一合同 ID 格式
- **建议**：统一为 `ZH02*` 格式（因为 `invoices`/`payments`/`supplier_contracts` 都在用）
- **例外**：`contracts` 表中 `SGSC*` 格式的合同 ID 保留（作为 `sgsc_id` 字段），但 `contract_id` 字段统一为 `ZH02*`

#### 1.2 建立双向映射表
在 `contract_id_mapping` 表中建立 `SGSC*` ↔ `ZH02*` 的双向映射：

```sql
-- 确保 mapping 表有双向映射
SELECT project_id_zh, contract_id FROM contract_id_mapping
WHERE project_id_zh LIKE 'ZH02%' OR contract_id LIKE 'SGSC%'
LIMIT 10;
```

#### 1.3 统一关联字段
- `payments.contract_id`：通过 `contract_id_mapping` 表转换为 `ZH02*` 格式
- `invoices.project_id`：保持 `ZH02*` 格式（已统一）
- `supplier_contracts.project_id`：保持 `ZH02*` 格式（已统一）
- `contract_project_link.project_id`：保持 `ZH02*` 格式（已统一）

---

### Step 2：OCR 数据清洗

#### 2.1 `expiry_date` 归一化
增加类似 `sign_date` 的归一化逻辑：

```python
# 清洗 expiry_date 中的 OCR 噪声
def clean_expiry_date(raw: str) -> str | None:
    if not raw:
        return None
    # 如果是合同编号格式（含 / 或中文），则视为无效
    if '/' in raw or '合同' in raw or len(raw) > 20:
        return None
    # 尝试解析日期
    return normalize_date(raw)  # 复用 sign_date 的归一化函数
```

#### 2.2 清洗 `expiry_date` 字段
```sql
-- 先查异常值
SELECT contract_id, expiry_date FROM contracts
WHERE expiry_date IS NOT NULL
  AND (expiry_date LIKE '%/%' OR expiry_date LIKE '%合同%' OR LENGTH(expiry_date) > 20);

-- 清洗（设为 NULL）
UPDATE contracts SET expiry_date = NULL
WHERE expiry_date IS NOT NULL
  AND (expiry_date LIKE '%/%' OR expiry_date LIKE '%合同%' OR LENGTH(expiry_date) > 20);
```

#### 2.3 `sign_date` 补全
- 对剩余 15 份 `sign_date` 为 NULL 的合同，重新检查 OCR 文本
- 如果确实无签订日期，则在详情页标注"未识别"而非显示空白

---

### Step 3：建立正确的关联视图

#### 3.1 修复 `current_finance_view`
使用 `contract_id_mapping` 表做桥接：

```sql
CREATE VIEW current_finance_view AS
SELECT
  c.contract_id,
  c.project_name,
  COALESCE(fr.total_receipt, 0) AS total_receipt,
  COALESCE(fr.total_payment, 0) AS total_payment,
  COALESCE(fr.total_invoice, 0) AS total_invoice
FROM contracts c
LEFT JOIN (
  SELECT
    m.project_id_zh AS contract_id,  -- 通过 mapping 表转换
    SUM(CASE WHEN fr.type = 'receipt' THEN fr.amount ELSE 0 END) AS total_receipt,
    SUM(CASE WHEN fr.type = 'payment' THEN fr.amount ELSE 0 END) AS total_payment,
    SUM(CASE WHEN fr.type = 'invoice' THEN fr.amount ELSE 0 END) AS total_invoice
  FROM finance_records fr
  LEFT JOIN contract_id_mapping m ON fr.project_id = m.contract_id
  GROUP BY m.project_id_zh
) fr ON c.contract_id = fr.contract_id;
```

#### 3.2 建立 `invoice_contract_link` 视图
通过 `contract_id_mapping` 关联发票和合同：

```sql
CREATE VIEW invoice_contract_link AS
SELECT
  i.invoice_id,
  i.invoice_no,
  i.project_id AS invoice_project_id,
  m.contract_id AS sgsc_id,
  m.project_id_zh AS zh02_id,
  c.contract_id AS matched_contract_id
FROM invoices i
LEFT JOIN contract_id_mapping m ON i.project_id = m.project_id_zh
LEFT JOIN contracts c ON c.contract_id = m.project_id_zh
  OR c.sgsc_id = m.contract_id;
```

---

## 📂 涉及文件

### 数据库层
- `database/project_management.db`（需执行迁移脚本）
- `migrations/004_unify_contract_id_format.sql`（新增迁移文件）
- `migrations/005_clean_ocr_noise.sql`（新增迁移文件）

### 后端层
- `backend/routers/contracts.py`（修复 detail API 关联查询）
- `backend/routers/finance.py`（修复财务视图）
- `backend/routers/invoices.py`（修复发票-合同关联）

### 数据清洗脚本
- `.devtest/clean_expiry_date.py`（新增清洗脚本）
- `.devtest/unify_contract_id.py`（新增统一 ID 脚本）

---

## ✅ 验收标准

### Step 1 验收
- [ ] `contracts` 表 `contract_id` 字段统一为 `ZH02*` 格式（或保留 `SGSC*` 但有明确映射）
- [ ] `payments.contract_id` 能匹配到 `contracts.contract_id`（匹配率 > 95%）
- [ ] `invoice_contract_link` 视图能正确关联发票和合同（关联率 > 90%）

### Step 2 验收
- [ ] `expiry_date` 字段无 OCR 噪声（查询结果为 0 条异常）
- [ ] `sign_date` 字段填充率 > 90%（当前 70%）

### Step 3 验收
- [ ] `current_finance_view` 返回正确的财务汇总数据（人工核对 5 份合同）
- [ ] `invoice_contract_link` 视图能正确关联发票和合同（测试 10 条记录）

---

## 📝 实施顺序

1. **先做 Step 2**（OCR 清洗）：不影响现有功能，风险低
2. **再做 Step 1**（ID 统一）：需备份数据，风险中等
3. **最后做 Step 3**（关联视图）：依赖前两步完成

---

## 🔗 参考资料

- `docs/数据补全-合同条款调研与规律总结-20260709.md`（合同 ID 格式分析）
- `docs/DB结构优化设计-20260709.md`（数据库结构优化建议）
- `contract_id_mapping` 表（ID 映射关系）
