# OCR 全量数据提取与 DB 结构优化方案 v2.0

> 基于20份样本合同的深度内容审计 + DB逐字段质量扫描 + 合同类型模板分析

## 一、核心发现

### 1.1 三种合同类型，对应三种标准模板

| 类型 | DB分类 | 模板号 | 章节结构 | 关键差异 |
|------|--------|--------|----------|----------|
| **技术研发型** | 科研类 | `SGTYHT/24-JS-001` | 21个标准化章节(1~21) | ✅阶段计划 ✅经费预算表 ✅支付计划 ✅研究成果归属 |
| **一般服务型** | 服务类 | `SGTYHT/23-JS-004` | 14个章节(1~14) | ✅服务内容/方式/地点/期限 ✅验收标准 ❌无阶段/预算 |
| **物资采购型** | 服务类 | `SGTYHT/25-JS-004` | 与服务类相同 | ✅中标/成交通知书 ✅保修/质保条款 |

### 1.2 科研类合同(技术研发型)的标准化结构

```
1. 主要内容                     → service_content
  1.1 主要技术内容
  1.2 主要技术难点
2. 预期目标                     → service_content（与1合并）
3. 主要技术经济指标
4. 提供的最终成果               → deliverables 表
5. 进度计划内容及考核目标       → stages 表（含acceptance_criteria）
6. 项目经费                     → NEW: contract_budgets 表
7. 项目支付计划                 → payments 表（与阶段关联）
8. 转委托
9. 保密                         → contract_clauses (confidential)
10. 陈述与保证
11. 风险承担
12. 研究成果的归属              → contract_clauses (ip)
13. 相关技术服务
14. 违约责任                    → contract_clauses (penalty)
15~20. 变更/解除/争议/附件等
21. 特别约定
```

### 1.3 服务/采购类合同的标准化结构

```
1. 技术服务项目概要             → service_content
  1.1 目标
  1.2 内容
  1.3 服务方式                  → service_method
2. 技术服务具体要求
  2.1 服务地点                  → service_location
  2.2 服务期限                  → service_period
  2.3 服务进度
  2.4 服务质量要求
3. 甲方提供的工作条件
4. 组织与管理
5. 技术服务报酬及支付方式       → payments 表
6. 技术服务工作成果的验收       → acceptance_criteria/method/location
7. 知识产权                     → contract_clauses (ip)
8. 保密义务                     → contract_clauses (confidential)
9. 违约责任                     → contract_clauses (penalty)
10. 合同变更和解除
11. 争议解决                    → contract_clauses (dispute)
12~14. 定义/组成部分/其他
```

---

## 二、DB 存量数据质量问题

### 2.1 空字段统计（20份样本）

| 问题类型 | 涉及字段 | 占比 |
|----------|----------|------|
| **系统性缺失** | financial_id | 100% 全空 |
| **大量缺失** | service_method, service_location, acceptance_method/acceptance_location | >80% |
| **半数缺失** | acceptance_criteria, party_a_contact, party_a_phone, party_b_phone, project_leader | ~50% |
| **脏数据** | bidder = "振华"（实为中标方名误填）、subcontract_contact 填入无关人名 | 常见 |
| **占位符** | tax_inclusive = "0"（应为空或布尔值）、部分字段含 `/` | 多份 |

### 2.2 关联缺失

| 问题 | 发现 | 影响 |
|------|------|------|
| 科研类缺阶段 | 16/21 合同无阶段 | 甘特图、阶段详情全部空 |
| 科研类缺付款 | 16/21 合同无付款计划（科研类必有） | 付款计划卡片空 |
| 阶段-付款无关联 | 已有阶段+付款的2份合同(ZH02-202408007/601010)，stage_payment_link 均为空 | 无法融合展示 |
| 项目团队 | personnel 表0行、project_personnel 表0行 | 团队卡片无法展示 |

### 2.3 DB 结构问题

| 问题 | 建议 |
|------|------|
| contracts 表48列过臃肿 | 中标信息→拆 bid_info 表、分包→subcontracts表、变更→contract_changes表 |
| **缺少 contract_budgets 表** | 科研类6个经费科目 × 甲方/乙方/自筹，必须新建 |
| personnel/project_personnel 为空但有结构 | 需从OCR提取填充 |

---

## 三、提取规则（按合同类型区分）

### 3.1 科研类提取规则

| OCR章节 | 目标表/字段 | 提取方法 |
|----------|------------|----------|
| 1-3. 主要内容/预期目标/指标 | contracts.service_content | 合并提取，去掉编号前缀 |
| 4. 最终成果 | deliverables | 按"成果名称-类型-数量"逐条解析 |
| 5. 进度计划及考核目标 | stages | 按研究阶段编号解析(时间范围+考核目标+工作内容) |
| **6. 项目经费** | **NEW contract_budgets** | 按科目表解析(人工费/设备费/材料费/业务费… 含甲方拨款+乙方自筹) |
| 7. 项目支付计划 | payments (+ stage_payment_link) | 按支付阶段解析(金额+条件+时间) |
| 8-21. 条款 | contract_clauses | 按类别(category=ip/confidential/penalty/dispute)分类存储 |
| 封面头 | contracts(联系人/甲方乙方/金额) | 正则提取项目负责人、联系人、合同金额 |

### 3.2 服务类提取规则

| OCR章节 | 目标表/字段 | 提取方法 |
|----------|------------|----------|
| 1.2 服务内容 | contracts.service_content | 直接提取 |
| 1.3 服务方式 | contracts.service_method | 格式: `咨询服务`/`现场服务`/`驻场服务` |
| 2.1 服务地点 | contracts.service_location | 直接提取 |
| 2.2 服务期限 | contracts.service_period | 含起止日期 |
| 5. 报酬及支付方式 | payments | 按支付阶段解析（通常与阶段无关，纯按时间/里程碑） |
| 6. 验收标准 | contracts.acceptance_criteria/method/location | 三字段分别提取 |
| 7-11. 条款 | contract_clauses | 按类别分类 |

### 3.3 物资采购型提取规则

| OCR章节 | 目标表/字段 | 提取方法 |
|----------|------------|----------|
| 与服务类相同部分 | 同上 | 同上 |
| **中标通知书**（合同附件） | **NEW bid_info 表** | 提取成交供应商、成交金额、中标日期、项目编号 |
| **保修条款** | contracts.warranty_months / quality_bond_pct | 提取质保期/质保金比例 |

---

## 四、执行计划

### 第1步：DB结构变更（新建表）
- [ ] 新建 `contract_budgets` 表
- [ ] 新建 `bid_info` 表（替代 contracts 中的 bidder/bid_amount/bid_date）
- [ ] 新建 `contract_changes` 表（替代 contracts.change_history）

### 第2步：批量提取脚本 (ocr_extract_all.py)
- [ ] 科研类：10份有OCR的科研合同 → stages/payments/budgets/clauses/deliverables
- [ ] 服务/采购类：21份有OCR的服务合同 → payments/clauses/acceptance/service_fields
- [ ] 条款合并去重：contract_clauses 按合同+类别去重
- [ ] 联系人/电话清洗：从OCR头信息提取甲方/乙方联系人+电话
- [ ] 中标信息提取：从OCR附件提取中标通知书数据

### 第3步：数据验证
- [ ] 对比OCR原文与DB写入内容
- [ ] 检查阶段-付款关联完整性
- [ ] 检查科研类合同预算表完整性

### 第4步：前端展示改造
- [ ] 付款+阶段融合展示（阶段表每行显示对应付款金额+状态）
- [ ] 条款折叠面板合并（违约/IP/保密/争议 一个 collapse）
- [ ] 经费预算表卡片（科研类独有）
- [ ] 项目团队卡片
