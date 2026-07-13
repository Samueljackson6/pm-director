# 企查查 MCP 积分消耗测试

**测试时间**: 2026-07-13
**测试企业**: 北京振华永创智能科技有限公司

---

## 查询策略：低积分优化版

### 阶段1: 基础信息（预计 1-2 积分）
1. `get_company_by_query` - 企业实体识别
2. `get_company_registration_info` - 工商信息

### 阶段2: 补充信息（预计 1-2 积分）
3. `get_company_profile` - 企业简介
4. `get_contact_info` - 联系方式

### 阶段3: 知识产权（预计 1-2 积分）
5. `get_trademark_info` - 商标信息
6. `get_software_copyright_info` - 软件著作权

### 阶段4: 风险扫描（预计 1-2 积分）
7. `get_company_risk_scan` - 风险扫描聚合

---

## 避免的高积分查询

- ❌ `get_shareholder_info` - 股东信息（高积分）
- ❌ `get_actual_controller` - 实际控制人（高积分）
- ❌ `get_beneficial_owners` - 受益所有人（高积分）
- ❌ `get_financial_data` - 财务数据（高积分）
- ❌ `get_patent_info` - 专利信息（高积分）

---

## 预计总消耗: 5-8 积分

(相比之前的 20+ 积分，节省 60% 以上)
