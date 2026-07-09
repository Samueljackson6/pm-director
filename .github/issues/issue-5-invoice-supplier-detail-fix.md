# Issue #5：发票/供应商详情跳转回归 + 页面内容丰富

## 问题描述
发票列表点击后未跳转到发票详情页，供应商管理点击后跳转报错。另外供应商页面需丰富内容。

## 子问题清单

### 5.1 发票详情跳转失效
- **现状**：发票列表点击后无反应或未跳转
- **期望**：点击发票行跳转到发票详情页（`/web/invoices/detail?id=<id>`）
- **相关文件**：
  - `ui-vben/apps/web-antd/src/views/invoices/list.vue`
  - `ui-vben/apps/web-antd/src/views/invoices/detail.vue`

### 5.2 供应商详情跳转报错
- **现状**：供应商列表点击后跳转报错
- **期望**：点击供应商行跳转到供应商详情页（`/web/suppliers/detail?id=<id>`）
- **相关文件**：
  - `ui-vben/apps/web-antd/src/views/suppliers/list.vue`
  - `ui-vben/apps/web-antd/src/views/suppliers/detail.vue`

### 5.3 供应商页面内容丰富
- **现状**：供应商详情页信息量少
- **期望**：
  - 展示企业基本信息（可通过企查查/天眼查等工具爬取）
  - 关联合同列表（该供应商的所有合同）
  - 关联发票列表（该供应商的所有发票）
  - 关联付款记录
  - 企业风险评估（诉讼、失信、经营异常等）
- **相关文件**：
  - `ui-vben/apps/web-antd/src/views/suppliers/detail.vue`
  - `backend/routers/suppliers.py`（需新增企业信息查询 API）

## 优先级
高（功能回归 + 新需求）

## 相关 PR
- PR #25：发票/供应商详情跳转修复（可能回归）

## 验收标准
- [ ] 发票列表点击跳转详情页正常
- [ ] 供应商列表点击跳转详情页正常
- [ ] 供应商详情页展示企业基本信息
- [ ] 供应商详情页关联合同/发票/付款记录
- [ ] 企业信息查询 API 可用（企查查/天眼查）
