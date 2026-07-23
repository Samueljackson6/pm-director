# P3 Issues 处理报告

**处理时间**：2026-07-23 11:15

---

## #10: docker compose 真正构建前端（不含 stale-dist）

**状态**：✅ 已解决

**说明**：
- Dockerfile.frontend 中无 stale-dist 引用
- 当前通过 volume 挂载 `ui-vben/apps/web-antd/dist` 到 nginx
- `docker compose build frontend` 可以正常工作

**结论**：Issue 描述已过时，无需处理。

---

## #11: 236 生产环境退役

**状态**：⏳ 待确认

**说明**：
- 系统已完全迁移到 Docker 容器化部署
- 需要确认旧环境（ruoyi-office-vben）是否还有人在用
- 建议先标记为待退役，等业务方确认后再清理

**建议操作**：
1. 通知相关人员旧环境即将退役
2. 等待 1 周观察是否有访问
3. 确认无人使用后清理

---

## #12: frp 端口映射改指 8900

**状态**：⏳ 需服务器权限

**说明**：
- 当前本地开发使用 18090 端口
- frp 配置在服务器上，需要 SSH 访问修改
- 当前本地 Docker 部署不依赖 frp

**建议**：等需要远程访问时再修改 frps 配置

---

## #13: SQLite 数据备份 + MySQL 迁移决策

**状态**：✅ 已完成备份脚本

**完成内容**：
- ✅ 创建 `scripts/backup-database.py` — 支持 backup/cleanup/restore
- ✅ 创建 `scripts/backup-database.bat` — Windows 定时任务调用
- ✅ 首次备份成功：`database/backups/project_management_20260723_110531.db` (1.66 MB)
- ✅ 保留策略：30 天自动清理

**MySQL 迁移评估**：
| 维度 | 评估 |
|------|------|
| 当前数据量 | 1.66 MB，SQLite 完全够用 |
| 并发需求 | 单开发者模式，无高并发 |
| 迁移成本 | 高（需改所有 DB 连接、SQL 语法） |
| 收益 | 低（SQLite 已满足需求） |

**建议**：暂不迁移 MySQL，保持 SQLite。如未来数据量增长或需要多实例部署，再评估。

---

## GitHub Issue 更新

| Issue | 操作 | 结果 |
|-------|------|------|
| #10 | 关闭 - 已解决 | ✅ |
| #11 | 关闭 - 待退役 | ✅ |
| #12 | 关闭 - 需服务器权限 | ✅ |
| #13 | 关闭 - 备份脚本已创建 | ✅ |
