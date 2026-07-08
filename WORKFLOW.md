# 合同管理系统 · 开发工作流

> 更新: 2026-07-08 | 环境: 本地开发 + 远程236部署
> 
> ⚠️ **所有前端开发（路由/菜单/组件/页面）必须阅读 `docs/vben-framework-rules.md` 遵循 Vben 框架规范**
> 
> 📖 Agent 入口文档：`CLAUDE.md`
>
> 🚨 **开发交付强制流程**：代码审查 → 本地Docker验证 → Playwright测试 → 汇报 → 确认后提交PR（详见 `docs/本地Docker环境维护规范.md`）
>
> 🗑️ **磁盘维护**：每周清理Docker构建缓存，<20GB时执行深度清理（详见 `docs/本地Docker环境维护规范.md` §2）

---

## 一、环境总览

| 环境 | 位置 | 用途 | 启动方式 | 关闭方式 |
|------|------|------|----------|----------|
| **本地开发** | `D:\Tare-workspace\pm-director\` | 编码、构建、自测 | 手动 | 手动 |
| **Docker 测试** | Docker Desktop | 后端容器化测试 | `docker compose up -d` | `docker compose down` |
| **236 生产** | 192.168.0.236 | 生产部署 | systemd / nohup | systemd |
| **GitHub** | `github.com/Samueljackson6/pm-director` | 代码托管 | — | — |

## 二、端口分配

| 服务 | 本地开发 | 236生产 | 说明 |
|------|---------|---------|------|
| FastAPI 后端 | 8800 | 8800 | SQLite 只读 API |
| Vben 仪表盘(旧版) | — | 5888 | 备用(旧版 ui-dashboard) |
| Vben 自定义前端 | — | 5777 | 自定义 Vben 页面(待部署) |
| RuoYi-Vben | — | 5666 | 独立项目，与本系统无关 |

## 三、开发流程

### 3.1 后端开发（FastAPI）

```bash
# 本地开发（Windows 原生 Python）
cd D:\Tare-workspace\pm-director
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8800 --reload
# 访问 http://localhost:8800/docs (Swagger)
```

### 3.2 Docker 测试

```bash
# 启动 Docker 测试环境
cd D:\Tare-workspace\pm-director
docker compose up -d
# 访问 http://localhost:8800/

# 关闭释放资源
docker compose down
```

### 3.3 前端开发（Vben Admin v5）

> Vben Admin v5 框架是独立项目（通过 npm create / git clone 获得），**不在** pm-director 仓库内。
> pm-director 只包含自定义 UI 代码，位于 `ui/` 目录。

**开发流程**：
```bash
# Vben 框架项目路径（独立）
cd /home/samuel/.openclaw/workspace/pm-director/ui-vben/apps/web-antd/

# 将 ui/src/ 下的自定义文件复制到框架对应位置
# 然后启动 dev server
pnpm dev  # → http://localhost:5777

# 构建
pnpm -F @vben/web-antd build

# 部署到 236
scp dist.zip 236:/tmp/
ssh 236 "unzip /tmp/dist.zip -d /home/samuel/ui-vben/apps/web-antd/dist/"
```

### 3.4 代码规范

| 规范 | 要求 |
|------|------|
| Vue 样式 | Composition API + `<script setup>` |
| 组件库 | Ant Design Vue (通过 Vben 封装) |
| HTTP | `requestClient` (由 `#/api/request` 导出) |
| 路由 | `src/router/routes/modules/*.ts` |
| 视图 | `src/views/*/index.vue` |
| API 模块 | `src/api/*.ts` |
| 响应格式 | `{code: 0, data: {...}}` |

### 3.5 API 模块写法（ui/src/api/）

```typescript
import { requestClient } from '#/api/request';

export function getContractsApi(params?: any) {
  return requestClient.get('/contracts', { params });
}
```

### 3.6 路由模块写法（ui/src/router/routes/modules/）

```typescript
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [{
  meta: { icon: 'lucide:file-text', order: 1, title: 'Contracts', ignoreAccess: true },
  name: 'Contracts', path: '/contracts',
  children: [{
    name: 'ContractList', path: 'list',
    component: () => import('#/views/contracts/index.vue'),
    meta: { title: 'All Contracts', ignoreAccess: true }
  }]
}];
export default routes;
```

### 3.7 组件写法（ui/src/views/）

```vue
<template>
  <a-card title="Title">
    <a-table :columns="cols" :data-source="items" row-key="id" />
  </a-card>
</template>
<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { getXxxApi } from '#/api/xxx'

const items = ref<any[]>([])
const cols = [{ title: 'Name', dataIndex: 'name' }]

onMounted(async () => {
  const r: any = await getXxxApi()
  items.value = r?.items || []
})
</script>
```

## 四、测试流程

```bash
# 后端 API 测试（直接访问）
curl http://localhost:8800/api/stats
curl http://localhost:8800/api/contracts?page=1&size=5

# Docker 测试
cd D:\Tare-workspace\pm-director
docker compose up -d
curl http://localhost:8800/api/stats
docker compose down
```

## 五、部署流程（236 生产服务器）

```bash
# 1. 后端部署（FastAPI）
ssh 236
cd /home/samuel/.openclaw/workspace/pm-director
git pull  # 或手动同步文件
pkill -f "uvicorn backend.main" || true
nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8800 > /tmp/pm-director.log 2>&1 &

# 2. Vben 前端构建部署（仅自定义页面更新时）
# 见 3.3 节

# 3. 验证
curl http://192.168.0.236:8800/api/stats
```

## 六、Git 规范

```
feat(模块): 简短说明

- 改动点1
- 改动点2
```

## 七、文件结构

```
D:\Tare-workspace\pm-director\
├── backend\main.py              ← FastAPI 后端
├── database\project_management.db ← SQLite 数据库
├── ui\                           ← Vben 自定义前端代码（框架独立存放）
│   ├── src\api\                  ← API 模块
│   │   ├── contracts.ts
│   │   ├── invoices.ts
│   │   ├── suppliers.ts
│   │   ├── request.ts
│   │   └── index.ts
│   ├── src\views\                ← 页面组件
│   │   ├── contracts\index.vue
│   │   ├── contracts\detail.vue
│   │   ├── invoices\index.vue
│   │   └── suppliers\index.vue
│   └── src\router\routes\modules\ ← 路由模块
│       ├── contracts.ts
│       ├── invoices.ts
│       └── suppliers.ts
├── tools\                        ← 工具脚本（OCR识别、合同提取等）
├── scripts\                      ← 数据脚本
├── docs\                         ← 项目文档
├── Dockerfile                    ← Python 3.11-slim
├── docker-compose.yml            ← 后端容器化
└── WORKFLOW.md                   ← 本文档
```
