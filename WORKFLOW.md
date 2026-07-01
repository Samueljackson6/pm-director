# 合同管理系统 · 开发工作流

> 更新: 2026-07-01 | 环境: 本地开发 + 远程236部署

---

## 一、环境总览

| 环境 | 位置 | 用途 | 启动方式 | 关闭方式 |
|------|------|------|----------|----------|
| **本地开发** | `D:\Tare-workspace\pm-director\` | 编码、构建、自测 | 手动 | 手动 |
| **Docker/WSL** | docker-desktop | 测试环境容器 | `wsl -d docker-desktop` | `wsl --shutdown` |
| **236服务器** | 192.168.0.236 | 生产部署 | systemd/nohup | systemd |
| **GitHub** | `github.com/Samueljackson6/pm-director` | 代码托管 | — | — |

## 二、端口分配

| 服务 | 本地开发 | 236生产 | 说明 |
|------|---------|---------|------|
| FastAPI后端 | 8800 | 8800 | SQLite 只读API |
| Vben仪表盘 | 5777 | 5777 | Ant Design Vue |
| 简易仪表盘 | — | 5888 | 备用(旧版) |
| RuoYi-Vben | — | 5666 | 独立项目 |

## 三、开发流程

### 3.1 开始新功能

```bash
# 1. 启动WSL/Docker测试环境（按需）
wsl -d docker-desktop

# 2. 本地开发（直接Windows）
cd D:\Tare-workspace\pm-director\vben
pnpm dev  # 启动Vben dev server → http://localhost:5777

# 3. 构建验证
pnpm -F @vben/web-antd build

# 4. Git提交
git add .
git commit -m 'feat(模块): 说明'
git push
```

### 3.2 代码规范

| 规范 | 要求 |
|------|------|
| Vue 样式 | Composition API + `<script setup>` |
| 组件库 | Ant Design Vue (通过 Vben 封装) |
| HTTP | `requestClient` (由 `#/api/request` 导出) |
| 路由 | `src/router/routes/modules/*.ts` |
| 视图 | `src/views/*/index.vue` |
| API 模块 | `src/api/*.ts` |
| 响应格式 | `{code: 0, data: {...}}` |

### 3.3 API 模块写法

```typescript
import { requestClient } from '#/api/request';

export function getContractsApi(params?: any) {
  return requestClient.get('/contracts', { params });
}
```

### 3.4 路由模块写法

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

### 3.5 组件写法

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
# 启动WSL测试环境
wsl -d docker-desktop

# 在WSL中部署测试
wsl -d docker-desktop -- docker run ...

# 运行Playwright测试（Windows原生）
cd D:\Tare-workspace\pm-director
npx playwright test

# 验证后关闭测试环境释放资源
wsl --shutdown
```

## 五、部署流程

```bash
# 1. 本地构建
cd D:\Tare-workspace\pm-director\vben
pnpm -F @vben/web-antd build

# 2. 复制到236
scp dist.zip 236:/tmp/
ssh 236 "unzip /tmp/dist.zip -d /home/samuel/.../ui-vben/apps/web-antd/dist/"

# 3. 重启服务
ssh 236 "pkill -f 'python3 -m http.server 5777'; cd /.../dist && python3 -m http.server 5777 &"

# 4. 验证
curl http://192.168.0.236:5777/

# 5. 关闭WSL释放资源
wsl --shutdown
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
├── backend\main.py         ← FastAPI 后端
├── database\*.db           ← SQLite 数据库
├── vben\apps\web-antd\src\
│   ├── api\                ← API模块
│   │   ├── contracts.ts
│   │   ├── invoices.ts
│   │   └── suppliers.ts
│   ├── views\              ← 页面组件
│   │   ├── contracts/
│   │   ├── invoices/
│   │   └── suppliers/
│   ├── router\routes\modules\  ← 路由模块
│   │   ├── contracts.ts
│   │   ├── invoices.ts
│   │   └── suppliers.ts
│   └── api\request.ts      ← requestClient配置
├── docs\vben\              ← Vben官方文档
└── WORKFLOW.md             ← 本文档
```
