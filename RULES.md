# 🎯 核心规则

> 此文件在每次会话开始时自动注入
> 最后更新：2026-07-03

---

## ⚠️⚠️⚠️ 最高铁律：跨项目基础设施协议

**违反后果**：影响 RuoYi Office 项目正常运行，数据永久丢失

**参考文档**：`D:\Tare-workspace\RuoYi Office Vben fSamuel\CROSS_PROJECT_INFRA.md`

### ❌ 绝对禁止

- 停止/重启/修改 `ruoyi-mysql`、`ruoyi-redis` 容器
- 使用 `root` 用户连接数据库
- 访问 RuoYi Office 的数据库或数据
- 创建新的 MySQL/Redis 容器
- 执行 `DROP DATABASE` / `FLUSHALL`
- 使用 `docker compose down` / `rm -f`（会误删他人容器）
- 在 compose 中使用 `network_mode: host`

### ✅ 必须遵守

- 只操作自己的容器：`pm-director-backend`、`pm-director-frontend`
- 使用自己的数据库用户：`pm_user` / `pm_director` 库
- Redis Key 加 `pm:` 前缀，使用 DB 1
- 敏感信息通过 `.env` 注入
- Docker 容器命名使用 `<项目>-<服务>` 格式

### ✏️ 协作修改通知

如果 pm-director 有涉及共享基础设施的变更需要通知 RuoYi Office，**必须去 RuoYi 项目的 `CROSS_PROJECT_INFRA.md` 文件中进行更新说明**（位于 `D:\Tare-workspace\RuoYi Office Vben fSamuel\CROSS_PROJECT_INFRA.md`）。这是两个项目之间唯一的协作沟通通道。

---

## 🚨 Vben Admin 5 框架开发规则 ⭐（2026-07-08 新增）

**违反后果**：路由 404、页面白屏、菜单不显示、构建失败、框架拦截

**参考文档**：`docs/vben-framework-rules.md`（完整版，含代码示例）

### 核心原则

1. **本项目使用 `accessMode: 'backend'`** — 路由由后端 API 控制，不是前端 module 文件
2. **新增页面 = 后端 + 前端两步**：① 在 `views/` 下创建 `.vue` 文件；② 在 `backend/routers/auth.py` 的 `menus` 中添加菜单项
3. **VxeTable 禁用 slot 解构** — 必须从 `#/adapter/vxe-table` 导入，用 `:formatter` 代替 `#default="{ row }"`
4. **后端修改后必须 `docker compose build backend`** — 源码不在卷上，在镜像里
5. **前端修改后只需 `pnpm build`** — 容器挂载宿主 dist 目录，无需 restart

### 启动必读

```bash
read docs/vben-framework-rules.md
```

所有涉及前端路由、菜单、组件、页面新增的任务，**必须先阅读 Vben 框架规则文档**。

---

## 🚨 开发交付流程铁律 ⭐（2026-07-08 新增）

**违反后果**：未验证的代码合并到生产导致事故

**参考文档**：`docs/本地Docker环境维护规范.md`（完整流程 + 命令）

### 每个开发任务的强制流程

```
开发 → 代码审查 → 本地Docker环境验证 → Playwright测试 → 汇报 → 确认后提交PR
```

**任何一步不可跳过。**

### ❌ 绝对禁止

- ❌ 跳过 Playwright 测试直接汇报"完成"
- ❌ 未在本地 Docker 环境验证直接提 PR
- ❌ Docker 磁盘 < 20GB 还无视继续构建
- ❌ 不询问用户直接 push 到 main 分支

### ✅ 必须遵守

- 每个改动必须在本地 Docker 环境（`http://localhost:8900/web/`）验证
- 必须用 Playwright 模拟用户操作测试（`cd .devtest && node playwright-t9.mjs`）
- 测试必须 0 FAIL / 0 控制台错误才算通过
- 每周执行一次 `docker builder prune --all --force`
- D 盘可用空间 < 20GB 时执行磁盘清理

### 汇报模板

```
做了什么：
验证结果：X PASS / X FAIL / X 控制台错误
Playwright摘要：...
是否提交 PR？
```

---

## ⚠️ 飞书表格增量维护铁律

**违反后果**：数据永久丢失，无法恢复

参见 MEMORY.md 完整说明。

---

## ⚠️ 统计数据铁律

**违反后果**：数据错误，误导决策

参见 MEMORY.md 完整说明。

---

## 📋 技能列表

完整技能列表见：`SKILLS.md`

---

*此文件由系统自动维护*
