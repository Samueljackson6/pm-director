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
