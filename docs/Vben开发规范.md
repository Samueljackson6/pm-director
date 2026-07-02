# Vben Admin 5 开发规范（pm-director 定制版）

> **更新**：2026-07-02
> **Vben 版本**：5.7.0
> **官方文档**：https://doc.vben.pro/
> **官方文档本地副本**：`<RuoYi-Office>/docs/vben-official/`（待同步）

---

## 一、Vben 官方文档索引

所有 Vben 框架相关开发必须遵循官方规范。以下为官方文档索引：

| 主题 | 官方链接 | 本地参考 | 优先级 |
|------|---------|---------|--------|
| 快速开始 | https://doc.vben.pro/guide/introduction/quick-start.html | - | ⭐⭐⭐ |
| **路由和菜单** | https://doc.vben.pro/guide/essentials/route.html | - | ⭐⭐⭐ |
| **构建与部署** | https://doc.vben.pro/guide/essentials/build.html | - | ⭐⭐⭐ |
| **服务端交互** | https://doc.vben.pro/guide/essentials/server.html | - | ⭐⭐⭐ |
| **Vxe Table 表格** | https://doc.vben.pro/components/common-ui/vben-vxe-table.html | - | ⭐⭐⭐ |
| 本地开发 | https://doc.vben.pro/guide/essentials/development.html | - | ⭐⭐ |
| 配置 | https://doc.vben.pro/guide/essentials/settings.html | - | ⭐⭐ |
| 权限 | https://doc.vben.pro/guide/in-depth/access.html | - | ⭐⭐ |
| 目录说明 | https://doc.vben.pro/guide/project/dir.html | - | ⭐⭐ |
| 样式 | https://doc.vben.pro/guide/essentials/styles.html | - | ⭐ |
| 图标 | https://doc.vben.pro/guide/essentials/icons.html | - | ⭐ |
| 国际化 | https://doc.vben.pro/guide/in-depth/locale.html | - | ⭐ |
| Vben Form 表单 | https://doc.vben.pro/components/common-ui/vben-form.html | - | ⭐⭐ |

---

## 二、核心规范

### 2.1 路由规范

**文件位置**：`src/router/routes/modules/*.ts`

**基本结构**：
```typescript
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [{
  name: 'ModuleName',           // 路由名称（唯一）
  path: '/module-name',         // 路由路径
  meta: {
    icon: 'lucide:icon-name',   // 菜单图标
    order: 1,                   // 菜单排序
    title: 'ModuleTitle',       // 显示标题
    ignoreAccess: true,         // 跳过权限验证（开发期使用）
  },
  children: [{
    name: 'ModuleList',
    path: 'list',
    component: () => import('#/views/module-name/index.vue'),
    meta: { title: 'List', ignoreAccess: true }
  }]
}];

export default routes;
```

**`#/` 路径别名**：Vben 框架自动将 `#/` 映射到 `src/`，如 `#/views/xxx` → `src/views/xxx`

### 2.2 API 服务规范

**文件位置**：`src/api/*.ts`

**使用 `requestClient`（而非 `baseRequestClient`）**：
```typescript
import { requestClient } from '#/api/request';

// GET 请求 - requestClient 自动解包 {code: 0, data: T} → T
export async function getContractsApi(params?: any) {
  return requestClient.get('/contracts', { params });
}
```

**`requestClient` vs `baseRequestClient` 区别**：

| 客户端 | 响应返回 | 说明 |
|--------|---------|------|
| `requestClient` | 自动解包 `data` 字段 | `{code:0, data:{items}}` → `{items}` |
| `baseRequestClient` | 原始响应 | `{code:0, data:{items}}` → 不处理 |

### 2.3 页面组件规范

#### 列表页：使用 `useVbenVxeGrid`

**标准模板**：
```vue
<script lang="ts" setup>
import type { VxeGridProps } from '#/adapter/vxe-table';
import { useVbenVxeGrid } from '#/adapter/vxe-table';
import { getContractsApi } from '#/api/contracts';

interface RowType {
  contract_id: string;
  project_name: string;
  // ... 其他字段
}

const gridOptions: VxeGridProps<RowType> = {
  columns: [
    { field: 'contract_id', title: '合同编号', width: 180 },
    { field: 'project_name', title: '项目名称', minWidth: 200 },
    { field: 'contract_amount', title: '金额(万元)', width: 120, formatter: 'formatMoney' },
  ],
  proxyConfig: {
    ajax: {
      // 自动处理分页请求，requestClient 已解包 data
      query: async ({ page }) => {
        const data = await getContractsApi({ page: page.currentPage, pageSize: page.pageSize });
        return { items: data.items, total: data.total };
      },
    },
  },
  toolbarConfig: { refresh: true, zoom: true },
};

const [Grid] = useVbenVxeGrid({ gridOptions });
</script>

<template>
  <Grid />
</template>
```

#### 详情页：使用 Vben 页面布局

**标准模板**：
```vue
<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getContractDetailApi } from '#/api/contracts';
import { useVbenVxeGrid } from '#/adapter/vxe-table';
import type { VxeGridProps } from '#/adapter/vxe-table';

const route = useRoute();
const detail = ref<any>(null);

onMounted(async () => {
  detail.value = await getContractDetailApi(route.params.id as string);
});
</script>

<template>
  <div class="p-4">
    <VbenPage title="合同详情">
      <a-descriptions :column="2" bordered :data="detail" />
    </VbenPage>
  </div>
</template>
```

### 2.4 响应格式约定

后端 API 必须遵循 Vben 的响应格式：

```typescript
// 成功响应
{ code: 0, data: T, message: 'success' }

// 分页列表
{ code: 0, data: { items: T[], total: number, page: number, size: number }, message: 'success' }

// 错误响应
{ code: -1, message: 'error description' }
```

---

## 三、当前页面合规分析（2026-07-02）

| 文件 | 合规状态 | 问题 |
|------|---------|------|
| `ui/src/api/contracts.ts` | ❌ 不合规 | 使用 `baseRequestClient`，应改为 `requestClient` |
| `ui/src/api/invoices.ts` | ❌ 不合规 | 同上 |
| `ui/src/api/suppliers.ts` | ❌ 不合规 | 同上 |
| `ui/src/views/contracts/index.vue` | ❌ 不合规 | 使用 `a-table`，应改为 `useVbenVxeGrid` |
| `ui/src/views/contracts/detail.vue` | ❌ 不合规 | 缺少 Vben 页面布局包装 |
| `ui/src/views/invoices/index.vue` | ❌ 不合规 | 使用 `a-table`，应改为 `useVbenVxeGrid` |
| `ui/src/views/suppliers/index.vue` | ❌ 不合规 | 自定义卡片布局，应改为 `useVbenVxeGrid` |
| 路由文件 (3个) | ✅ 基本合规 | 使用 `ignoreAccess: true` + `#/` 路径，需确认 meta 完整性 |

---

## 四、236 部署环境

| 项目 | 配置 |
|------|------|
| Vben 框架路径 | `/home/samuel/.openclaw/workspace/pm-director/ui-vben/` |
| 应用目录 | `apps/web-antd/` |
| API 地址 | `http://192.168.0.236:8800/api` |
| 前端端口 | 5777 |
| 构建命令 | `pnpm -F @vben/web-antd build` |
| 部署方式 | `dist/` → `python3 -m http.server 5777` |

---

## 五、开发工作流

```bash
# 1. 修改自定义文件（在 pm-director/ui/ 中编辑）
# 2. 同步到 236 Vben 框架
scp -r ui/src/* 236:/home/samuel/.../ui-vben/apps/web-antd/src/

# 3. 在 236 上构建
ssh 236 "cd /home/samuel/.../ui-vben && pnpm -F @vben/web-antd build"

# 4. 重启前端服务
ssh 236 "pkill -f 'http.server 5777'; cd ui-vben/apps/web-antd/dist && nohup python3 -m http.server 5777 &"

# 5. 验证
curl http://192.168.0.236:5777/
```

---

## 六、常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 页面渲染空白 | 组件未正确使用 Vben 封装 | 使用 `useVbenVxeGrid` 替代 `a-table` |
| API 返回格式不对 | `responseReturn` 配置不一致 | 使用 `requestClient`（自动解包） |
| 路由不显示 | 权限/菜单配置 | 添加 `ignoreAccess: true` |
| 构建失败 | 路径别名错误 | 使用 `#/` 别名确保正确 |

---

**遵守原则**：所有 Vben 框架上的开发必须严格遵循官方规范，不得混用 Ant Design 原生组件与 Vben 封装组件。
