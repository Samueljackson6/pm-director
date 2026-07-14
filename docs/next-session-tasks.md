# 下一步计划 —— 2026-07-15

> 本文档记录明天待处理的后续事项

---

## 当前系统状态

- **前端**: `http://localhost:18090/web/`（Docker nginx）
- **后端**: `http://localhost:18080`（Docker FastAPI）
- **CI/CD**: ✅ 已修复，自动部署到 236 生产环境
- **数据库**: `database/project_management.db`

---

## 待办事项

### 1. 老环境退役 ⏳

**脚本已创建**: `scripts/retire-old-environment.sh`

**执行前检查**:
```bash
# 确认新环境完全可用
curl http://localhost:18090/web/
curl http://localhost:18080/health

# 查看老环境容器状态
docker ps -a | grep -E "frontend|backend|nginx"
```

**执行命令**:
```bash
cd D:/Tare-workspace/pm-director
./scripts/retire-old-environment.sh
```

---

### 2. SQLite 备份配置 ⏳

**脚本已创建**: `scripts/sqlite-backup.sh`
**策略文档**: `docs/sqlite-backup-decision.md`

**配置 cron 定时任务**:
```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天凌晨 2 点备份）
0 2 * * * /home/samuel/.openclaw/workspace/pm-director/scripts/sqlite-backup.sh
```

**或使用 systemd timer**（推荐）:
```bash
# 创建 systemd service
sudo nano /etc/systemd/system/pm-director-backup.service
sudo nano /etc/systemd/system/pm-director-backup.timer
sudo systemctl enable --now pm-director-backup.timer
```

---

### 3. 阶段2：数据契约与清洗 ⏳

参考文档：`docs/audits/系统全量审计与改造基线-2026-07-13.md`

**待处理项**:
- [ ] 外键约束恢复（当前 167 条违规）
- [ ] 金额单位统一标注（元/万元）
- [ ] 数据清洗脚本

---

### 4. 可选优化

- [ ] 前端测试覆盖率提升
- [ ] 合同详情页 UI 重设计（参考 `docs/合同详情页整体改造方案-20260711.md`）
- [ ] 服务内容 6 字段前端展示优化

---

## 关键文件

| 文件 | 用途 |
|------|------|
| `scripts/retire-old-environment.sh` | 老环境退役脚本 |
| `scripts/sqlite-backup.sh` | SQLite 备份脚本 |
| `docs/sqlite-backup-decision.md` | 备份策略决策 |
| `docs/ci-deployment-fix-20260714.md` | CI 修复记录 |
| `.github/workflows/ci.yml` | CI/CD 配置 |

---

## 快速命令

```bash
# 查看容器状态
docker ps

# 查看前端日志
docker logs pm-director-frontend --tail 20

# 查看后端日志
docker logs pm-director-backend --tail 20

# 重新部署
cd D:/Tare-workspace/pm-director
docker compose down && docker compose up -d

# 运行前端测试
cd ui-vben/apps/web-antd && pnpm vitest run

# 运行后端测试
cd backend && python -m pytest -q
```
