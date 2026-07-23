# RFC: suppliers 表甲方/乙方数据分类

**RFC 编号**：RFC-001
**创建时间**：2026-07-23
**状态**：待评审
**关联 Issue**：[#57](https://github.com/Samueljackson6/pm-director/issues/57)

---

## 问题描述

`suppliers` 表同时存储了**甲方（客户/业务单位）**和**乙方（实际供应商/承揽商）**的数据，但没有任何字段可以区分两者。

### 当前影响

| 影响范围 | 问题 |
|---------|------|
| 供应商管理模块 | 列表中甲方和乙方混在一起，无法分类筛选 |
| 台账同步 | `contracts.party_a` 为纯文本，无法通过供应商表关联 |
| 财务统计 | 甲方回款（客户回款）和乙方付款（供应商付款）逻辑不同，混在一起会导致统计错误 |

### 现状数据

- `suppliers` 表共约 40 条 active 记录
- 其中约 22 条是甲方（客户单位），占 40%
- 其余是乙方（实际供应商/承揽商）
- `category` 字段原为"未分类"，无实际意义

---

## 方案对比

### 方案 A：suppliers 表新增 category 字段（推荐）

```sql
ALTER TABLE suppliers ADD COLUMN category TEXT DEFAULT 'vendor' 
    CHECK (category IN ('client', 'vendor'));
```

**优点：**
- 改动最小，兼容现有数据
- 前端只需加 Tab 切换即可区分
- API 增加过滤参数即可

**缺点：**
- 需要数据迁移脚本
- contracts.party_a 仍不关联 suppliers（需额外外键）

### 方案 B：拆分为两个表

```
clients 表 — 甲方（客户单位）
suppliers 表 — 乙方（实际供应商）
```

**优点：**
- 数据结构最清晰
- 字段可以针对不同角色定制

**缺点：**
- 改动大，涉及多处代码修改
- 台账同步逻辑需要重写
- 前端需要大量改造

### 方案 C：保留现状，前端做区分

在 contracts 表中维护 party_a/party_b 的完整信息，不在 suppliers 表中区分。

**优点：**
- 零改动

**缺点：**
- 供应商管理模块始终无法正确工作
- 台账同步始终失败

---

## 推荐方案：A + 渐进式实施

### Phase 1：数据层（1天）
1. 给 `suppliers` 表加 `category` 字段
2. 编写数据迁移脚本，根据上下文分类
3. 更新数据库文档

### Phase 2：API 层（1天）
4. `/api/suppliers` 增加 `?category=client|vendor` 过滤
5. 台账同步逻辑区分处理

### Phase 3：前端层（1-2天）
6. 供应商列表增加 Tab：甲方客户 / 乙方供应商
7. 台账页面区分展示

### Phase 4：长期优化（可选）
8. 评估是否需要拆分 contracts.party_a 为外键关联

---

## 工作量评估

| 阶段 | 工作量 | 风险 |
|------|--------|------|
| Phase 1 | S（约 0.5-1 天） | 低 |
| Phase 2 | M（约 1 天） | 中 |
| Phase 3 | M（约 1-2 天） | 低 |
| Phase 4 | L（待定） | 高 |
| **总计** | **3-5 天** | **中** |

---

## 决策建议

1. **短期**：先实施 Phase 1-2，解决台账同步和 API 过滤问题
2. **中期**：Phase 3 前端改造，提升用户体验
3. **长期**：Phase 4 视业务需求决定是否拆分

**请业务方确认**：
- 甲方是否真的需要作为"供应商"管理？
- 如果甲方只是合同参考信息，是否可以简化处理？

---

## 相关文件

| 文件 | 路径 |
|------|------|
| 供应商路由 | `D:\Tare-workspace\pm-director\backend\routers\suppliers.py` |
| 供应商发票路由 | `D:\Tare-workspace\pm-director\backend\routers\supplier_invoices.py` |
| 数据库定义 | `D:\Tare-workspace\pm-director\backend\database.py` |
| 供应商列表页 | `D:\Tare-workspace\pm-director\ui-vben\apps\web-antd\src\views\suppliers\list\index.vue` |
| 供应商发票页 | `D:\Tare-workspace\pm-director\ui-vben\apps\web-antd\src\views\supplier-finance\invoices\index.vue` |
| 供应商付款页 | `D:\Tare-workspace\pm-director\ui-vben\apps\web-antd\src\views\supplier-finance\payments\index.vue` |
