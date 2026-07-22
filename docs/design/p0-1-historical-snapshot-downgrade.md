# 历史快照表降级为只读参考的说明

> 日期：2026-07-20  
> 状态：**已确认**  
> 关联 Issue：[#48 P0-1](https://github.com/Samueljackson6/pm-director/issues/48)

---

## 一、降级范围

以下三张表从"核心业务数据"降级为"只读历史快照参考"：

| 表 | 数据来源 | 当前用途 | 降级后定位 |
|-----|---------|---------|-----------|
| `finance_records` | Excel 批量导入 | 财务快照 | 历史财务快照，每周更新，只读参考 |
| `current_finance_view` | `finance_records` 最新快照聚合 | 财务视图 | 只读视图，用于历史对比 |
| `master_table` | Excel 导出总表 | 运营总表 | 原始运营数据参考 |

---

## 二、为什么必须保留这些表

> **重要说明**：这些历史快照在系统初期会保持每周更新，开发和维护时需要参考这些数据。

### 2.1 开发参考

新页面开发时，需要快速查看历史财务数据作为：
- Mock 数据生成基准
- 页面展示验证依据
- 金额换算测试用例

如果没有这些表，每次开发新页面都需要手动构造测试数据，效率极低且容易与真实业务脱节。

### 2.2 手动维护参考

运营人员可能需要：
- 从 Excel 导出总表进行人工核对
- 对比系统数据与手工台账的差异
- 追溯某笔金额的历史来源

### 2.3 渐进迁移支持

系统初期不可能一次性清洗所有历史数据。这些快照表提供过渡期支持：
- 允许新旧数据并存
- 便于发现数据口径差异
- 为后续自动化迁移提供验证基准

### 2.4 审计追溯价值

当主数据被修改后，历史快照可作为变更前的参考点：
- 对比修改前后的金额变化
- 追溯财务数据的来源和依据
- 满足内部审计和合规要求

---

## 三、使用规范

### 3.1 读写权限

| 场景 | 是否允许读取 | 是否允许写入 |
|------|------------|------------|
| API 查询 | ✅ 允许（作为参考数据） | ❌ 禁止 |
| 页面展示 | ✅ 允许（标注"历史快照"） | ❌ 禁止 |
| 开发调试 | ✅ 允许 | ❌ 禁止 |
| 手动维护 | ✅ 允许（通过 Excel 导入） | ❌ 禁止通过 API |
| 主数据修正 | ✅ 允许作为参考 | ❌ 禁止直接修改 |

### 3.2 API 响应标注

所有返回历史快照数据的 API 必须在响应中标注：

```json
{
  "data": { ... },
  "source": "finance_snapshot",
  "snapshot_date": "2026-W26",
  "warning": "此数据为历史快照，仅供参考，不作为当前业务真值"
}
```

### 3.3 前端展示标注

涉及历史快照数据的页面必须显示提示：

> ⚠️ 此数据来源于历史财务快照，可能与当前业务数据存在差异。请以合同、发票、回款等交易流水为准。

---

## 四、历史快照库演变为审计库的可行性分析

### 4.1 当前局限

| 表 | 局限 |
|-----|------|
| `finance_records` | 有 `batch_id` 和 `import_time`，但没有变更前后对比 |
| `master_table` | 没有版本控制，无法追溯历史状态 |
| `current_finance_view` | 是视图而非独立快照，无法保留历史 |

### 4.2 审计库演化建议

#### 方案 A：增加变更日志表（推荐，成本低）

新增 `data_change_log` 表：

```sql
CREATE TABLE IF NOT EXISTS data_change_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    change_type TEXT NOT NULL,  -- INSERT / UPDATE / DELETE
    old_value TEXT,             -- JSON 格式
    new_value TEXT,             -- JSON 格式
    changed_by TEXT,            -- 操作人
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT                 -- 变更原因
);
```

**优点**：
- 实现成本低，只需在写操作时记录日志
- 为后续审计打基础
- 不改变现有表结构

**缺点**：
- 无法追溯历史快照本身的变更
- 需要确保所有写操作都记录日志

#### 方案 B：建立快照版本表（中期实施）

新增 `finance_snapshot_history` 表：

```sql
CREATE TABLE IF NOT EXISTS finance_snapshot_history (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    snapshot_date DATE NOT NULL,
    import_time TIMESTAMP NOT NULL,
    record_count INTEGER,
    total_invoice_amount REAL,
    total_payment_amount REAL,
    source_file TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**优点**：
- 完整保留每次快照的元数据
- 可追溯快照之间的变化趋势
- 为审计提供时间线

**缺点**：
- 需要额外存储空间
- 需要定期清理旧快照

#### 方案 C：归档 Excel 文件（推荐，简单有效）

每次导入的 Excel 文件归档到 `uploads/finance_snapshots/`：

```
uploads/finance_snapshots/
├── finance_snapshot_20260720.xlsx
├── finance_snapshot_20260727.xlsx
└── finance_snapshot_20260803.xlsx
```

**优点**：
- 最简单，无需数据库改动
- 保留原始数据，可随时复核
- 符合审计要求

**缺点**：
- 文件管理需要规范
- 无法直接 SQL 查询

### 4.3 实施优先级

| 优先级 | 措施 | 理由 |
|--------|------|------|
| P0 | 归档 Excel 文件 | 成本最低，收益最高，避免数据丢失 |
| P1 | 增加变更日志表 | 为后续审计打基础，成本低 |
| P2 | 建立快照版本表 | 等主数据稳定后再实施 |

### 4.4 结论

> **建议**：先实施方案 C（归档 Excel 文件）和方案 A（增加变更日志表），暂不实施方案 B（快照版本表）。
>
> 理由：
> 1. 当前优先级应在 P0-2/P0-3 业务闭环，不宜过早投入审计库建设
> 2. Excel 文件归档是最基本的数据保护措施，应立即实施
> 3. 变更日志表成本低，可为后续审计提供基础
> 4. 快照版本表可在主数据稳定后作为独立任务实施

---

## 五、与主数据的关系

### 5.1 数据优先级

```
交易流水（invoices/receipts/payments） > 主档（contracts/projects/suppliers） > 历史快照（finance_records/current_finance_view/master_table）
```

### 5.2 冲突处理规则

当历史快照与主数据/交易流水不一致时：

1. **以交易流水为准**：发票、回款、付款记录是最终真值
2. **主档为参考**：合同金额、项目总金额用于校验
3. **历史快照仅作对照**：不得覆盖或修改主数据和交易流水

### 5.3 开发时的使用方式

| 开发场景 | 使用方式 |
|---------|---------|
| 新页面开发 | 从历史快照读取 mock 数据 |
| 金额换算测试 | 对比历史快照与交易流水 |
| 页面验证 | 使用历史快照作为预期结果 |
| 用户培训 | 展示历史快照帮助理解业务 |
| 问题排查 | 追溯历史数据变化 |

---

## 六、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 开发人员误用历史快照作为真值 | 数据错误 | API 响应明确标注"历史快照" |
| 前端未显示警告提示 | 用户误解 | 强制要求在相关页面显示警告 |
| 历史快照过期未及时清理 | 占用存储 | 设置保留期限（如 2 年） |
| Excel 文件丢失 | 无法追溯 | 定期备份到 Git 或云存储 |

---

> **文档版本**：v1.0  
> **下次更新**：主数据稳定后评估是否实施快照版本表  
> **关联文档**：`docs/audits/p0-1-database-analysis-20260720.md`、`docs/design/p0-1-amount-unit-strategy.md`
