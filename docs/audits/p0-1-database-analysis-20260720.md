# P0-1 数据库分析与数据契约决策报告

> 编制：pm-director（项目总监）  
> 日期：2026-07-20  
> 状态：**待业务评审**  
> 关联 Issue：[#48 P0-1：数据真值、金额单位与关系契约](https://github.com/Samueljackson6/pm-director/issues/48)

---

## 一、执行摘要

本报告基于对 `database/project_management.db` 的完整 schema 分析、数据抽样和业务逻辑审计，得出以下核心结论：

1. **金额单位混用已确认**：系统存在万元/元两种单位并存，需统一 API 输出为元
2. **主数据源已识别**：`contracts`/`projects`/`suppliers` 为主档，`invoices`/`receipts`/`payments` 为交易流水
3. **财务快照需降级**：`finance_records`/`current_finance_view`/`master_table` 为 Excel 导入的历史快照，应标记为只读参考
4. **contract_id_mapping 定位明确**：SGSC ↔ ZH 编号映射表，应以 ZH 编号为 canonical ID
5. **历史快照可演变为审计库**：建议在保留原始数据的同时增加变更追踪机制

---

## 二、数据库基线

### 2.1 环境状态

| 项目 | 值 |
|------|-----|
| Docker 后端 | `pm-director-backend` Up 8h, healthy |
| Docker 前端 | `pm-director-frontend` Up 8h |
| 当前 DB SHA256 | `45353085257E5EE93CBD98889911631B7A793D51474559C6DBCA5EB6859C7C64` |
| 接管基线 SHA256 | `8651DC7EA351EBCA9FC2D6E718B04A70A373759AEB9795C709CBA6F1DA154849` |
| 差异原因 | `get_db()` 每次连接执行 `_init_tables()` 创建 `supplier_contacts` 表 |

### 2.2 表清单（36 张表）

```
bid_info (34)
contract_budgets (22)
contract_changes (0)
contract_clauses (131)
contract_files (40)
contract_id_mapping (32)
contract_project_link (45)
contract_type_attributes (29)
contracts (45)
deliverables (71)
finance_records (43)
invoice_files (0)
invoice_receipt_link (25)
invoices (87)
master_table (16)
payment_vouchers (0)
payments (84)
personnel (34)
project_personnel (101)
project_status (29)
projects (50)
qcc_alert_config (0)
qcc_basic_info (1)
qcc_company_profile (1)
qcc_external_investments (2)
qcc_risk_alerts (0)
qcc_risk_scan (1)
qcc_software_copyrights (34)
qcc_sync_log (2)
receipts (34)
sqlite_sequence (12)
stage_payment_link (0)
stages (46)
supplier_contacts (0)
supplier_contracts (23)
supplier_payments (0)
suppliers (55)
```

---

## 三、金额单位分析

### 3.1 各表单位现状

| 表/字段 | 单位 | 示例值 | 证据 |
|---------|------|--------|------|
| `contracts.contract_amount` | **万元** | 496.5995, 125.085, 85.95 | 合同主档 |
| `projects.total_contract_amount` | **万元** | 496.5995, 125.085 | 与 contracts 基本一致 |
| `payments.planned_amount` | **万元** | 496.5995, 220.793 | 与 contracts 一致 |
| `payments.paid_amount` | **万元** | 100.0, 0.0 | 与 planned 同量级 |
| `finance_records.contract_amount` | **万元** | 125.085, 496.5995 | Excel 导入快照 |
| `finance_records.invoice_total` | **万元** | 112.5765, 159.9179 | 从元转换而来 |
| `finance_records.payment_total` | **万元** | 112.5765, 94.8526 | 从元转换而来 |
| `current_finance_view.contract_total` | **万元** | 57.23364, 75.44 | finance_records 最新快照 |
| `current_finance_view.invoice_total` | **万元** | 57.2336, 75.44 | 同上 |
| `current_finance_view.payment_total` | **万元** | 0.0, 67.44 | 同上 |
| `invoices.amount` | **元** | 400000, 808356, 15500 | 发票明细 |
| `receipts.amount` | **元** | 753300, 372465 | 回款明细 |
| `master_table.含税金额` | **元** | 4965995, 859500 | 早期 Excel 总表 |
| `master_table.不含税金额` | **元** | 4684900.94, 810849.06 | 同上 |
| `supplier_contracts.contract_amount` | **万元** | 217.4811, 100.0 | 供应商合同 |

### 3.2 关键验证：contracts vs master_table

`contracts.contract_amount` vs `master_table.含税金额` 的比值精确为 **0.0001**（即 1/10000）：

```
ZH02-202601011: contracts=496.5995 万元, master=4965995 元 → ratio=0.0001
ZH02-202601010: contracts=220.7930 万元, master=2207930.4 元 → ratio=0.0001
ZH02-202601005: contracts=85.9500 万元, master=859500 元 → ratio=0.0001
```

**结论**：`master_table` 是原始元数据（单位：元），`contracts` 是转换后的万元值。

### 3.3 典型冲突案例：ZH02-202509025

| 数据源 | 金额 | 单位 | 说明 |
|--------|------|------|------|
| `contracts.contract_amount` | 125.085 | 万元 | 合同主档 |
| `projects.total_contract_amount` | 125.085 | 万元 | 项目主档 |
| `invoices` outbound 合计 | 1,125,765 | 元 | 3 张客户发票 |
| `receipts` 合计 | 1,125,765 | 元 | 2 笔回款 |
| `finance_records.invoice_total` | 112.5765 | 万元 | 与 invoices 合计一致 ✓ |
| `payments.planned_amount` 合计 | 8.3976 | 万元 | ⚠️ 仅 2 条记录，远小于合同额 |

**问题**：付款计划不完整，仅记录了部分阶段付款，未覆盖全部合同金额。

### 3.4 金额单位策略决策

> **决策（用户确认，2026-07-20）**：数据库保持万元/元混合现状，API 层统一输出为元。

#### 理由

1. **避免破坏历史数据**：直接修改数据库可能导致财务快照、历史报表不一致
2. **最小化代码变更**：只需在 API 输出层做单位转换，不改动数据写入逻辑
3. **前端统一接收元**：前端展示时自行转换为万元（÷10000），符合用户阅读习惯

#### 实施规则

| 数据类型 | 数据库单位 | API 输出单位 | 转换逻辑 |
|---------|-----------|-------------|---------|
| 合同金额 | 万元 | 元 | ×10000 |
| 项目总金额 | 万元 | 元 | ×10000 |
| 付款计划 | 万元 | 元 | ×10000 |
| 发票金额 | 元 | 元 | 不变 |
| 回款金额 | 元 | 元 | 不变 |
| 财务快照 | 万元 | 元 | ×10000 |
| 供应商合同 | 万元 | 元 | ×10000 |

#### 前端处理

- 所有金额字段在展示时统一除以 10000 转为万元显示
- 输入框接受元或万元，由用户选择，后端统一存储原单位
- 金额对比时自动换算到同一单位

---

## 四、主数据源与镜像表判断

### 4.1 数据层级架构

```
┌─────────────────────────────────────────────────────────────┐
│                    源头真值层                                │
│  PDF 扫描件 = 影像原件 → DOCX = OCR 文本层                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    系统主档层（唯一真值）                      │
│  contracts / projects / suppliers                           │
│  - 合同主档：contract_id (ZH 编号), contract_amount          │
│  - 项目主档：project_id, total_contract_amount               │
│  - 供应商主档：supplier_id, supplier_name                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    关系/关联层                                │
│  contract_id_mapping / contract_project_link                 │
│  supplier_contracts / invoice_receipt_link                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    交易流水层                                 │
│  invoices / receipts / payments / supplier_payments          │
│  - 发票：amount (元), direction, invoice_type                │
│  - 回款：amount (元), receipt_date                           │
│  - 付款计划：planned_amount (万元), paid_amount              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    履约执行层                                 │
│  stages / deliverables / contract_clauses / contract_budgets │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    历史快照层（只读参考）                      │
│  finance_records / current_finance_view / master_table       │
│  - 从 Excel 批量导入的财务快照                                │
│  - 每周更新，作为历史参考和审计依据                            │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 各表定位

| 层级 | 表 | 定位 | 读写权限 |
|------|-----|------|---------|
| 源头真值 | PDF/DOCX | 合同原件 | 只读 |
| 主档 | `contracts` | 合同主档 | 读写 |
| 主档 | `projects` | 项目主档 | 读写 |
| 主档 | `suppliers` | 供应商主档 | 读写 |
| 关系 | `contract_id_mapping` | SGSC↔ZH 编号映射 | 读写 |
| 关系 | `contract_project_link` | 合同-项目关联 | 读写 |
| 关系 | `supplier_contracts` | 供应商-合同关联 | 读写 |
| 关系 | `invoice_receipt_link` | 发票-回款关联 | 读写 |
| 交易 | `invoices` | 发票流水 | 读写 |
| 交易 | `receipts` | 回款流水 | 读写 |
| 交易 | `payments` | 付款计划流水 | 读写 |
| 交易 | `supplier_payments` | 供应商付款流水 | 读写 |
| 履约 | `stages` | 履约阶段 | 读写 |
| 履约 | `deliverables` | 交付物 | 读写 |
| 履约 | `contract_clauses` | 合同条款 | 读写 |
| 履约 | `contract_budgets` | 经费预算 | 读写 |
| 快照 | `finance_records` | 财务快照（Excel 导入） | **只读** |
| 快照 | `current_finance_view` | 财务视图（finance_records 最新） | **只读** |
| 快照 | `master_table` | 运营总表（Excel 导出） | **只读** |
| 缓存 | `qcc_*` | 企查查数据缓存 | 读写 |

---

## 五、contract_id_mapping 分析

### 5.1 表用途

`contract_id_mapping` 是 **SGSC 内部编号 ↔ ZH 正式编号** 的映射表，用于跨表关联。

| 字段 | 说明 | 示例 |
|------|------|------|
| `project_id_zh` | ZH 前缀正式编号（**主键**） | `ZH02-202509025` |
| `project_id_sgsc` | SGSC 前缀内部编号 | `SGSCDK00XTJS250033` |
| `financial_id` | 财务系统编号 | `SGSCSDGXFZJS2600011` |
| `project_name` | 项目名称 | 自动填充或 NULL |
| `last_verified` | 最后核验时间 | 时间戳 |
| `source` | 来源 | `auto_mapping` / `auto_mapping_v2` / `amount_match` |

### 5.2 数据质量

- **总数**：32 条映射
- **自动匹配生成**：大部分 source 为 `auto_mapping` 或 `auto_mapping_v2`
- **名称缺失**：部分 `project_name` 为 NULL（自动匹配未填名称）
- **大小写不规范**：如 `SGsCYAFDSJJS2600004`、`susCL10oFCJS2600057`
- **截断 ID**：`ZH02-202604025` 对应 `SGSCCD`（不完整）

### 5.3 Canonical ID 策略

> **决策（用户确认，2026-07-20）**：以 ZH 编号为 canonical ID。

#### 规则

1. **ZH 编号为主键**：所有业务实体以 `ZH` 前缀编号为唯一标识
2. **SGSC 编号为别名**：`contract_id_mapping.project_id_sgsc` 存储 SGSC 别名
3. **跨表关联使用 ZH**：`contracts.contract_id`、`projects.project_id` 统一使用 ZH 编号
4. **历史数据兼容**：旧数据中的 SGSC 编号通过 mapping 表解析为 ZH

#### 清理计划

| 问题 | 处理方式 |
|------|---------|
| 大小写不规范 | 统一为大写 `SGSC` |
| 截断 ID | 标记为待人工确认，暂不删除 |
| NULL project_name | 尝试从 contracts/projects 表回填 |
| NULL financial_id | 暂留空，后续从财务系统补充 |

---

## 六、历史快照表降级方案

### 6.1 降级范围

以下三张表从"核心业务数据"降级为"只读历史快照参考"：

| 表 | 当前用途 | 降级后定位 |
|-----|---------|-----------|
| `finance_records` | 财务快照（从 Excel 导入） | 历史财务快照，每周更新 |
| `current_finance_view` | 财务视图（finance_records 最新） | 只读视图，用于历史对比 |
| `master_table` | 运营总表（Excel 导出） | 原始运营数据参考 |

### 6.2 为什么需要保留这些表

> **重要说明（用户强调，2026-07-20）**：这些历史快照在系统初期会保持每周更新，开发和维护时需要参考这些数据。

#### 理由

1. **开发参考**：新页面开发时，需要快速查看历史财务数据作为 mock 数据或验证基准
2. **手动维护**：运营人员可能需要从 Excel 导出总表进行人工核对
3. **审计追溯**：当主数据被修改后，历史快照可作为变更前的参考点
4. **渐进迁移**：系统初期不可能一次性清洗所有历史数据，快照表提供过渡期支持

#### 使用规范

| 场景 | 是否允许读取 | 是否允许写入 |
|------|------------|------------|
| API 查询 | ✅ 允许（作为参考数据） | ❌ 禁止 |
| 页面展示 | ✅ 允许（标注"历史快照"） | ❌ 禁止 |
| 开发调试 | ✅ 允许 | ❌ 禁止 |
| 手动维护 | ✅ 允许（通过 Excel 导入） | ❌ 禁止通过 API |
| 主数据修正 | ✅ 允许作为参考 | ❌ 禁止直接修改 |

### 6.3 审计库演化建议

> **建议（综合评估，2026-07-20）**：历史快照库可以逐步演变为审计库，但需要增加变更追踪机制。

#### 当前局限

- `finance_records` 有 `batch_id` 和 `import_time`，但没有变更前后对比
- `master_table` 没有版本控制，无法追溯历史状态
- `current_finance_view` 是视图，不是独立快照，无法保留历史

#### 建议改进

1. **增加快照版本表**：`finance_snapshot_history`
   - 每次导入时保存完整快照
   - 包含 `snapshot_date`、`batch_id`、`created_at`
   
2. **增加变更日志表**：`data_change_log`
   - 记录主数据表的 INSERT/UPDATE/DELETE
   - 包含 `table_name`、`record_id`、`old_value`、`new_value`、`changed_by`、`changed_at`

3. **保留原始 Excel 文件**：
   - 每次导入的 Excel 文件归档到 `uploads/finance_snapshots/`
   - 文件名格式：`finance_snapshot_YYYYMMDD.xlsx`

#### 是否必要？

| 选项 | 建议 | 理由 |
|------|------|------|
| 立即实施完整审计库 | ⚠️ 暂缓 | 当前优先级应在 P0-2/P0-3 业务闭环 |
| 先增加变更日志表 | ✅ 推荐 | 成本低，收益高，为后续审计打基础 |
| 先归档 Excel 文件 | ✅ 推荐 | 简单有效，避免数据丢失 |
| 建立 finance_snapshot_history | 🔜 中期 | 等主数据稳定后再实施 |

---

## 七、P0-0 运行基线核查结果

### 7.1 Docker 环境

| 容器 | 状态 | 端口 |
|------|------|------|
| `pm-director-backend` | Up 8h, healthy | 18080→8800 |
| `pm-director-frontend` | Up 8h | 18090→80 |

### 7.2 数据库基线

| 项目 | 值 |
|------|-----|
| 文件大小 | 1,736,704 字节 |
| 当前 SHA256 | `45353085...C7C64` |
| 接管基线 SHA256 | `8651DC7E...4849` |
| 差异原因 | `get_db()` 执行 `_init_tables()` 创建 `supplier_contacts` 表 |

### 7.3 待修复：`_init_tables()` 风险

**问题**：`backend/database.py` 中的 `_init_tables()` 在每次写连接时自动创建表，导致数据库被修改。

**影响**：
- 数据库 SHA256 基线不一致
- 可能触发不必要的 DDL 操作
- 与 G003 严格只读原则冲突

**修复建议**：
1. 将建表逻辑移到显式迁移脚本（如 `scripts/migrate.py`）
2. `get_db()` 不再自动执行 `_init_tables()`
3. 启动时调用一次迁移脚本确保表存在

---

## 八、P0-0 构建产物指纹验证

### 8.1 当前问题（B-10）

交接文档指出：构建产物/容器/浏览器版本关系不可核验。

### 8.2 验证机制建议

1. **后端版本号**：`backend/main.py` 中已有 `SERVICE_VERSION = '0.1.0'`，需随发版更新
2. **前端构建指纹**：在 `ui-vben/apps/web-antd/dist/` 生成 `build-info.json`
   ```json
   {
     "build_time": "2026-07-20T10:00:00Z",
     "git_commit": "abc123",
     "version": "0.1.0"
   }
   ```
3. **Docker 镜像标签**：使用 `docker compose build --tag pm-director:0.1.0`
4. **服务健康检查**：`GET /health` 返回版本号，`GET /ready` 返回数据库状态

### 8.3 验证命令

```bash
# 后端版本
curl http://localhost:18080/health

# 前端构建信息
curl http://localhost:18090/web/build-info.json

# 数据库基线
sha256sum database/project_management.db
```

---

## 九、行动清单

### 9.1 立即可做（P0-0）

- [ ] 修复 `backend/database.py` 的 `_init_tables()` 风险
- [ ] 建立构建产物指纹验证机制
- [ ] 更新 `SERVICE_VERSION` 为当前版本

### 9.2 待业务确认后（P0-1）

- [ ] 制定金额单位转换的 API 设计规范
- [ ] 清理 `contract_id_mapping` 中的数据质量问题
- [ ] 标记 `finance_records`/`current_finance_view`/`master_table` 为只读参考

### 9.3 中期实施（P0-2+）

- [ ] 建立 `data_change_log` 变更日志表
- [ ] 归档 Excel 导入文件
- [ ] 实施 `finance_snapshot_history` 快照版本表

---

## 十、附录：关键 SQL 查询

### 10.1 验证金额单位一致性

```sql
-- contracts vs master_table
SELECT c.contract_id, 
       c.contract_amount as contracts_wan,
       mt.含税金额 as master_yuan,
       mt.含税金额 / c.contract_amount as ratio
FROM contracts c
LEFT JOIN master_table mt ON c.contract_id = mt.项目编号
WHERE c.contract_amount IS NOT NULL AND mt.含税金额 IS NOT NULL;
```

### 10.2 查找金额异常

```sql
-- 发票金额 > 合同金额 10 倍的项目
SELECT c.contract_id, c.contract_amount,
       SUM(i.amount) as invoice_total_yuan,
       SUM(i.amount) / (c.contract_amount * 10000) as ratio
FROM contracts c
LEFT JOIN invoices i ON c.contract_id = i.project_id
GROUP BY c.contract_id
HAVING ratio > 10;
```

### 10.3 财务快照最新批次

```sql
SELECT batch_id, COUNT(*) as cnt, MIN(import_time) as earliest, MAX(import_time) as latest
FROM finance_records
GROUP BY batch_id
ORDER BY latest DESC;
```

---

> **文档版本**：v1.0  
> **下次更新**：P0-1 业务评审通过后  
> **关联文档**：`docs/design/核心业务整改主计划-20260720.md`、`docs/handoff/核心业务整改-交接文档-20260720.md`
