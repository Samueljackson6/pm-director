# 合同详情页改造 —— 当前状态 & 待办事项

> 本文档提供给下一会话使用。**描述当前状态和已知问题，不预设具体 UI 方案**。
> 数据治理详情见 `docs/data-cleanup-report-2026-07-12.md`

---

## 当前系统状态

- **运行地址**: `http://localhost:18090/web/`（前端） / `http://localhost:18080`（后端 API）
- **登录**: admin / admin123
- **构建命令**: `cd ui-vben && pnpm run build:antd`（包名 `@vben/web-antd`，**不是** `web-antd`）
- **重启后端**: `docker compose restart backend`
- **重启前端**: `docker compose restart frontend`（nginx 挂载 `dist/`，构建后需重启）
- **数据库**: `database/project_management.db`（容器内 `/app/database/`）

---

## 数据层已完成的工作（今天）

### 阶段
- 科研类合同阶段从 1 开始编号（"合同签订之日" 是阶段1的起始日期，不再是独立 #0）
- 阶段名统一为"研究阶段5.1"~"5.N"
- `remarks`（主要内容）与 `acceptance_criteria`（考核目标）已分离，共修复 41 处混叠
- OCR 页码/模板编号/碎片字符已清除

### 服务内容
- contracts 表新增 `service_schedule`、`service_quality` 两列
- 22 个技术服务类合同的 `service_content` 已拆分为 6 个独立字段：
  - `service_content` — 1.2 技术服务的内容
  - `service_method` — 1.3 技术服务的方式
  - `service_location` — 2.1 技术服务地点
  - `service_period` — 2.2 技术服务期限
  - `service_schedule` — 2.3 技术服务进度（新）
  - `service_quality` — 2.4 技术服务质量要求（新）

### 付款
- 52 条付款截断已修复
- 科研类 33 条付款已重建阶段引用（"乙方完成研究阶段5.1~5.2约定内容..."）

### 团队 & 供应商
- `personnel` 表 34 人（从合同联系人去重）
- `project_personnel` 表 101 行关联
- `suppliers` 表 55 个（从合同甲乙方去重）

### 已知残余问题
- 2 个服务类合同的"阶段"实际是联系人信息行（无研究内容），需前端过滤或删除
- ZH02-202508013 的 service_content 在原始 OCR 时损坏（PDF 为扫描件，需 OCR 管道重新提取）
- 部分阶段 `remarks` 为空但 `acceptance_criteria` 有内容——已从 ac 推导填充，但语义可能不完美

---

## 待办事项

### 任务1: 编辑功能完善
**现状**: 编辑弹窗只能改合同基本信息（名称/金额/日期/甲乙方/联系人）。
**不覆盖**: 阶段内容、考核目标、服务字段（method/schedule/quality）、付款描述。

**问题**:
- 科研类合同需要编辑：各阶段的"阶段内容"和"考核目标"、经费预算
- 技术服务类合同需要编辑：服务方式/进度/质量要求（以及已有的地点/期限）
- 两类合同的编辑字段完全不同，需要根据 `project_type` 切换编辑表单
- 现有编辑表单的文本框缺少字段名标签，用户不知道每个框对应什么字段

### 任务2: 合同详情页 UI 重设计
**现状**: 当前 `detail.vue` 的布局和样式比较基础，所有合同共用同一个模板。

**参考**: EPBT 项目 v8 版 demo 的公告详情页风格（可在新会话中查看 EPBT 项目代码）。

**分析点**（由新会话自行判断）:
- 科研类和技术服务类合同是否需要两套不同的详情页模板？
- 信息摆放顺序、折叠策略、卡片间距、字体层级如何优化？
- 是否需要将"服务内容"从左边信息栏中独立出来？

### 任务3: 服务内容 6 字段前端展示
**今天已做**: 数据库层面已将 22 个技术服务类合同的服务内容拆分为 6 个独立字段。
**待分析**: 
- 前端当前是否已展示这 6 个字段？还是仍然只显示一个合并的 `service_content`？
- 如果未展示，新会话需要判断展示方式和优先级
- `service_schedule` 和 `service_quality` 是新增字段，前端可能完全没有对应的渲染逻辑

### 任务4: 项目团队卡片
**今天已做**: `personnel` 表从空→34 人，`project_personnel` 从空→101 行关联。
**待分析**:
- 前端当前团队卡片展示的内容和价值如何？是否已使用新增的人员数据？
- 是否需要增加角色分类、颜色标记等视觉优化？

---

## 关键文件
| 文件 | 用途 |
|------|------|
| `ui-vben/apps/web-antd/src/views/contracts/detail.vue` | 详情页 |
| `ui-vben/apps/web-antd/src/api/contracts.ts` | API 调用 |
| `backend/routers/contracts.py` | 后端路由 |
| `database/project_management.db` | 数据库 |
| `.workbuddy/memory/MEMORY.md` | 项目规范 |
| `docs/data-cleanup-report-2026-07-12.md` | 数据治理详细报告 |
