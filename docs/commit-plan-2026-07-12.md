# 主仓库提交方案

**分支**: `feature/contract-detail-ui-refactor`
**分析时间**: 2026-07-12

---

## 改动分类总览

| 类别 | 数量 | 处理方式 |
|------|------|----------|
| 已修改跟踪文件 | 26 | 按功能分组提交 |
| 需要提交的新文件 | ~20 | 按功能分组提交 |
| 临时文件（不提交） | ~111 | 加入 .gitignore 或忽略 |

---

## 提交方案（分 3 个 commit）

### Commit 1: 合同详情页重构（P0-P3）

**核心改动**：合同详情页架构重构 + 甘特图修复

**已修改文件**：
- `ui-vben/apps/web-antd/src/views/contracts/components/stage-gantt.vue`
- `ui-vben/apps/web-antd/src/views/contracts/detail.vue`
- `ui-vben/apps/web-antd/src/views/contracts/index.vue`
- `backend/routers/contracts.py`

**新增文件**：
- `ui-vben/apps/web-antd/src/views/contracts/components/ServiceContent.vue`
- `ui-vben/apps/web-antd/src/views/contracts/components/ResearchContent.vue`

**Commit Message**:
```
feat(contracts): 详情页重构 + 甘特图修复

- P1: 外壳架构重构，拆分 ServiceContent/ResearchContent 子组件
- P2: 编辑弹窗补字段（阶段 remarks、服务 schedule/quality）
- P3: KPI 紧凑化、吸顶锚点条、卡片色条
- fix: 甘特图 bandHeight 边界计算修复（最后一个阶段条块不显示）
```

---

### Commit 2: 仪表盘与项目详情优化

**已修改文件**：
- `ui-vben/apps/web-antd/src/views/dashboard/overview/index.vue`
- `ui-vben/apps/web-antd/src/views/projects/detail.vue`
- `ui-vben/apps/web-antd/src/views/projects/index.vue`
- `ui-vben/apps/web-antd/src/api/dashboard.ts`
- `ui-vben/apps/web-antd/src/api/projects.ts`
- `backend/routers/dashboard.py`
- `backend/tests/test_dashboard.py`

**新增文件**：
- `ui-vben/apps/web-antd/src/views/dashboard/overview/components/`（目录）
- `ui-vben/apps/web-antd/src/views/dashboard/overview/dashboard-types.ts`
- `ui-vben/apps/web-antd/src/views/projects/__tests__/`（目录）

**Commit Message**:
```
feat(dashboard, projects): 仪表盘现代化 + 项目详情优化

- 仪表盘 KPI 卡片紧凑化
- 项目详情页结构优化
- 新增仪表盘组件和类型定义
```

---

### Commit 3: 其他视图与测试补全

**已修改文件**：
- `ui-vben/apps/web-antd/src/views/invoices/detail.vue`
- `ui-vben/apps/web-antd/src/views/suppliers/detail.vue`
- `ui-vben/apps/web-antd/src/api/invoices.ts`
- `ui-vben/apps/web-antd/src/api/suppliers.ts`
- `backend/routers/invoices.py`
- `backend/routers/suppliers.py`
- `backend/main.py`
- `backend/tests/conftest.py`
- `backend/tests/test_health.py`
- `.github/workflows/ci.yml`
- `.devtest/playwright-verify-all.mjs`

**新增文件**：
- `backend/tests/test_suppliers.py`
- `backend/tests/test_contract_detail_regressions.py`
- `ui-vben/apps/web-antd/src/views/invoices/__tests__/`（目录）
- `ui-vben/apps/web-antd/src/views/invoices/amount.ts`

**Commit Message**:
```
feat: 发票/供应商详情优化 + 测试补全

- 发票/供应商详情页结构优化
- 新增供应商测试、合同详情回归测试
- CI 健康检查改进
```

---

## 不提交的文件（建议处理）

### 加入 .gitignore
```
# 临时调试文件
.devtest/*.py
.devtest/*.json
.devtest/*.md
.devtest/*.cjs
.devtest/*.mjs
.debug_*.html
echarts.local.js
nul
overview.md

# 工作记忆
.workbuddy/

# 临时计划
.planning/
.github/plans/

# 数据迁移脚本（一次性）
scripts/analyze_*.py
scripts/fix_*.py
scripts/batch_*.py
scripts/clean_*.py
scripts/*_audit.py
scripts/import_finance*.py
scripts/repair_*.py
scripts/fuzzy_*.py
scripts/deep_*.py
scripts/quick_*.py
scripts/list_*.py
scripts/contract_cross_verify.py
scripts/contract_data_fix.py
scripts/extract_sgsc_contract.py
```

### 数据库不提交
`database/project_management.db` - 二进制数据库文件，建议撤销暂存

---

## 文档文件（可选提交）

以下文档可选择性提交：
- `docs/handover-2026-07-12.md` - 交接指引（建议提交）
- `docs/detail-refactor-p1-spec.md` - P1 规格
- `docs/detail-refactor-p3-spec.md` - P3 规格
- `docs/*.md` - 审计报告、改造方案等

建议：放在第 4 个 commit 单独提交文档
