# P0-0 构建产物指纹验证机制设计

> 日期：2026-07-20  
> 状态：**待业务评审**  
> 关联 Issue：[#47 P0-0](https://github.com/Samueljackson6/pm-director/issues/47)

---

## 一、问题背景（B-10）

交接文档指出：**构建产物/容器/浏览器版本关系不可核验**。

具体表现：
- 无法确认当前浏览器访问的是哪个版本的代码
- 无法确认 Docker 容器运行的是哪个构建产物
- CI/CD 产出的 `dist` 目录与部署到容器的产物可能不一致

---

## 二、设计方案

### 2.1 后端版本号

`backend/main.py` 已有 `SERVICE_VERSION = '0.1.0'`，需在每次发版时更新。

健康检查接口已返回版本号：

```python
@app.get('/health')
async def health_check() -> dict:
    return {
        'status': 'ok',
        'service': 'pm-director',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': SERVICE_VERSION,
    }
```

**验证命令**：
```bash
curl http://localhost:18080/health
```

### 2.2 前端构建指纹

在 `ui-vben/apps/web-antd/dist/` 目录下生成 `build-info.json`：

```json
{
  "build_time": "2026-07-20T10:00:00Z",
  "git_commit": "abc123def456",
  "git_branch": "main",
  "version": "0.1.0",
  "build_number": 42
}
```

**生成方式**：在 Vite 构建脚本中添加插件或 post-build 脚本。

**验证命令**：
```bash
curl http://localhost:18090/web/build-info.json
```

### 2.3 Docker 镜像标签

使用语义化版本标签：

```bash
docker compose build --tag pm-director-backend:0.1.0
docker tag pm-director-backend:0.1.0 pm-director-backend:latest
```

**验证命令**：
```bash
docker inspect pm-director-backend --format '{{.Config.Labels}}'
```

### 2.4 数据库基线

每次发版前记录数据库 SHA256：

```bash
sha256sum database/project_management.db > database/.baseline-$(date +%Y%m%d-%H%M%S).sha256
```

**验证命令**：
```bash
cat database/.baseline-latest.sha256
sha256sum -c database/.baseline-latest.sha256
```

---

## 三、验证流程

### 3.1 发版前检查清单

- [ ] 更新 `backend/main.py` 的 `SERVICE_VERSION`
- [ ] 执行 `pnpm run build:antd` 生成前端产物
- [ ] 确认 `dist/build-info.json` 已生成
- [ ] 记录数据库 SHA256 基线
- [ ] 执行 Docker 构建并打标签
- [ ] 部署到测试环境
- [ ] 验证 `/health` 和 `/web/build-info.json` 版本号一致
- [ ] 执行回归测试

### 3.2 运行时验证

| 检查项 | 命令 | 预期结果 |
|--------|------|---------|
| 后端版本 | `curl localhost:18080/health` | `version` 字段匹配发版记录 |
| 前端版本 | `curl localhost:18090/web/build-info.json` | `git_commit` 匹配发版记录 |
| 数据库基线 | `sha256sum database/project_management.db` | 与 `.baseline-latest.sha256` 一致 |
| Docker 镜像 | `docker inspect pm-director-backend` | 构建时间匹配发版时间 |

---

## 四、与 CI/CD 集成

### 4.1 GitHub Actions

在 CI 流水线中自动生成构建指纹：

```yaml
- name: Generate build info
  run: |
    echo "{\"build_time\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"git_commit\": \"${{ github.sha }}\", \"git_branch\": \"${{ github.ref_name }}\", \"version\": \"${{ steps.version.outputs.version }}\"}" > ui-vben/apps/web-antd/dist/build-info.json

- name: Record DB baseline
  run: |
    sha256sum database/project_management.db > database/.baseline-latest.sha256

- name: Build Docker image
  run: |
    docker compose build --tag pm-director-backend:${{ github.sha }}
```

### 4.2 部署脚本

`scripts/deploy-docker.sh` 中增加版本验证步骤：

```bash
#!/bin/bash
set -e

# 记录部署前数据库基线
sha256sum database/project_management.db > database/.baseline-deploy-$(date +%Y%m%d-%H%M%S).sha256

# 构建并部署
docker compose down
docker compose build
docker compose up -d

# 验证部署版本
BACKEND_VERSION=$(curl -s http://localhost:18080/health | python -c "import sys,json; print(json.load(sys.stdin)['version'])")
FRONTEND_COMMIT=$(curl -s http://localhost:18090/web/build-info.json | python -c "import sys,json; print(json.load(sys.stdin)['git_commit'])")

echo "Backend version: $BACKEND_VERSION"
echo "Frontend commit: $FRONTEND_COMMIT"

# 确认与 Git 提交一致
if [ "$FRONTEND_COMMIT" != "$(git rev-parse HEAD)" ]; then
    echo "ERROR: Frontend commit mismatch!"
    exit 1
fi
```

---

## 五、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 忘记更新版本号 | 无法追溯发版 | CI 流水线强制检查 |
| build-info.json 未生成 | 前端版本不可核验 | Dockerfile 中 COPY 前检查文件存在 |
| 数据库基线过期 | 无法确认是否被篡改 | 每次部署自动更新 `.baseline-latest.sha256` |
| CI 与部署环境不一致 | 部署的不是 CI 构建产物 | 部署脚本验证 git_commit 匹配 |

---

## 六、实施计划

| 阶段 | 任务 | 预计工时 |
|------|------|---------|
| 1 | 修改 Vite 构建脚本生成 `build-info.json` | 0.5 天 |
| 2 | 修改 `Dockerfile.frontend` 确保文件被 COPY | 0.5 天 |
| 3 | 更新 `deploy-docker.sh` 增加版本验证 | 0.5 天 |
| 4 | 编写单元测试验证版本一致性 | 0.5 天 |
| **合计** | | **2 天** |

---

> **文档版本**：v1.0  
> **下次更新**：实施完成后  
> **关联文档**：`docs/audits/p0-1-database-analysis-20260720.md`
