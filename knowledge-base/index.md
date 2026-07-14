# PM Director 知识库索引

> 本知识库记录项目开发过程中的关键知识、模式和决策。
> 所有 Agent 在完成任务后，应将新知识归档到相应目录。

---

## 目录结构

```
knowledge-base/
├── index.md              # 本文件 - 知识库索引
├── patterns/             # 代码模式和最佳实践
│   ├── route-patterns.md
│   ├── return-contract.md
│   └── component-patterns.md
├── archived/             # 已归档的知识（按日期）
│   └── 2026-07/
│       └── phase1-route-fix.md
└── decisions/            # 架构决策记录 (ADR)
    └── 001-backend-route-mode.md
```

---

## 快速查找

### 按主题

| 主题 | 文档 | 说明 |
|------|------|------|
| 路由规范 | `patterns/route-patterns.md` | 后端路由模式、路径格式 |
| 返回契约 | `patterns/return-contract.md` | 详情页返回逻辑规范 |
| 组件模式 | `patterns/component-patterns.md` | VxeTable、StateBlock 等 |
| 部署规范 | `../docs/部署规范.md` | Docker 部署流程 |
| 开发流程 | `../docs/开发流程规范.md` | PR、CI、验收流程 |
| 贡献约束 | `../docs/贡献约束.md` | 路由、命名、代码风格 |

### 按问题

| 问题 | 查找位置 |
|------|---------|
| 如何新增页面？ | `CLAUDE.md` → Vben 框架核心规则 |
| 路由 404 怎么排查？ | `patterns/route-patterns.md` → 常见问题 |
| 详情返回错误页面？ | `patterns/return-contract.md` |
| CI 检查失败？ | `../docs/开发流程规范.md` → CI 门禁 |
| 金额单位怎么处理？ | `../docs/贡献约束.md` → 金额单位规范 |

---

## 审计报告索引

| 日期 | 报告 | 主要发现 |
|------|------|---------|
| 2026-07-13 | `docs/audits/系统全量审计与改造基线-2026-07-13.md` | 四套基础关系失控 |
| 2026-07-13 | `docs/audits/菜单路由与返回链路矩阵-2026-07-13.md` | 路由无唯一真值 |
| 2026-07-13 | `docs/audits/阶段0完成报告-20260713.md` | 安全止血完成 |
| 2026-07-13 | `docs/audits/阶段1完成报告-20260713.md` | 路由基线修复完成 |

---

## 改造进度跟踪

```
阶段0: ✅ 完成 — 安全止血
  ├─ master 分支保护
  ├─ 数据库备份
  └─ PR #25 关闭

阶段1: ✅ 完成 — 路由与发布基线
  ├─ 供应商菜单修复
  ├─ 客户发票返回修复
  ├─ 旧路由重定向
  └─ PR #33 合并

阶段2: ✅ 完成 — 数据契约与清洗
  ├─ 外键违规清理 (167条 → 0条)
  ├─ 金额单位统一 (元 → 万元)
  ├─ 交付物去重
  └─ 提交: 93cfe80, b2bf4ec, 19498f7

阶段3: ⏳ 待开始 — 信息架构与UI
  ├─ 菜单重设计
  └─ 视觉规范建立
```

---

## P3 任务状态（2026-07-14 确认）

| Issue | 标题 | 状态 | 说明 |
|-------|------|------|------|
| T9 | 前端财务仪表盘接入 dashboard 接口 | OPEN | T8 已完成，待联调 |
| T10 | docker compose 真正构建前端 | OPEN | CI 部署失败 - @vben-core/design entry 问题 |
| T11 | 236 老环境退役 | OPEN | 待处理 |
| T12 | frp 公网穿透改指 8900 | OPEN | 待处理 |
| T13 | SQLite 备份策略 + MySQL 迁移决策 | OPEN | 已有备份，待完善策略 |

---

## CI 状态（2026-07-14）

最新提交: `5d62704` - fix: 修复 ruff E722 错误

| Job | 状态 |
|-----|------|
| Python Lint | ✅ 通过 |
| Backend Test (pytest) | ✅ 通过 |
| Frontend Test (vitest) | ✅ 通过 |
| UI Validate | ✅ 通过 |
| 部署到236 | ❌ 失败 (前端构建问题) |

---

## 搜索命令

```bash
# 搜索知识库
./scripts/search-knowledge.sh "路由"

# 搜索审计报告
grep -r "供应商" docs/audits/

# 搜索规范文档
grep -r "返回契约" docs/
```

---

## 归档规范

### 何时归档

- 完成一个阶段后
- 解决一个重要问题后
- 发现新的模式后

### 归档格式

```markdown
# 标题

日期：YYYY-MM-DD
类型：阶段完成 / 问题解决 / 模式发现
相关：Issue #xxx, PR #xxx

## 背景

<!-- 为什么需要这个知识 -->

## 内容

<!-- 核心内容 -->

## 教训

<!-- 学到了什么 -->

## 参考

<!-- 相关文档链接 -->
```

---

## 维护

- **更新频率**：每周整理一次
- **清理频率**：每月清理过时内容
- **责任人**：当前 Session 的 Agent
