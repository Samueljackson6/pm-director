# CI/CD 部署修复报告

> 日期：2026-07-14
> 状态：✅ 已完成

---

## 问题背景

CI 部署到 236 服务器时持续失败，前端和后端构建成功但容器启动失败。

---

## 问题排查

### 第一次失败：Docker 构建找不到 SCSS 文件
```
Can't find stylesheet to import.
```
**原因**：`.dockerignore` 排除了 `ui-vben` 源码目录

### 第二次失败：容器名称冲突
```
Error: container name "/pm-director-frontend" is already in use
```
**原因**：旧容器未被清理

### 第三次失败：`docker compose down` 未删除孤立容器
```
docker compose down --remove-orphans
# 仍然报容器冲突
```
**原因**：孤立容器不在当前 compose 项目管理范围内

### 第四次成功：强制删除容器
```yaml
docker compose down --remove-orphans 2>/dev/null || true
docker rm -f pm-director-frontend pm-director-backend 2>/dev/null || true
docker compose up -d
```

---

## 最终修复

文件：`.github/workflows/ci.yml`

```yaml
echo "=== 停止并移除旧容器 ==="
docker compose down --remove-orphans 2>/dev/null || true
# 强制删除可能存在的孤立容器
docker rm -f pm-director-frontend pm-director-backend 2>/dev/null || true

echo "=== 启动服务 ==="
docker compose up -d
```

---

## 部署结果

```
Frontend: HTTP 200 ✅
Backend:  HTTP 200 ✅
=== ✅ 审计通过 ===
```

---

## 已完成任务

| 任务 | 状态 |
|------|------|
| T9: 前端财务仪表盘接入 | ✅ 完成 |
| T10: docker compose 构建前端 | ✅ 完成 |
| T11+T12: 老环境退役脚本 | ✅ 已创建 |
| T13: SQLite 备份策略 | ✅ 已创建 |

---

## 创建的脚本

### 老环境退役脚本
- `scripts/retire-old-environment.sh` - 安全清理旧环境

### SQLite 备份脚本
- `scripts/sqlite-backup.sh` - 自动备份脚本
- `docs/sqlite-backup-decision.md` - 备份策略决策文档

---

## 提交记录

| Commit | 说明 |
|--------|------|
| `02feee7` | fix: 强制删除孤立容器后再启动 |
| `8f091a6` | fix: CI 部署前先停止旧容器避免名称冲突 |
| `5414163` | fix: 恢复 @vben-core/design 的原始 exports 配置 |
