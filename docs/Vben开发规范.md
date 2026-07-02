# Vben Admin 5 开发规范（pm-director 定制版）

> **更新**：2026-07-02
> **Vben 版本**：5.7.0
> **官方文档 **：https://doc.vben.pro/
> **本地文档索引**：`docs/vben-official-index.md`（**强制先读**）
> **GitHub 仓库**：https://github.com/vbenjs/vue-vben-admin
> **RuoYi-Office-Vben 基底**：https://gitee.com/yudaocode/yudao-ui-admin-vben

---

## 一、Vben 官方文档本地索引

**所有 Vben 框架相关的开发/维护/配置/发布，必须先查阅 `docs/vben-official-index.md` 找到对应主题，阅读官方说明后再动手。** 这是铁的纪律。

文档索引文件：**[`docs/vben-official-index.md`](./vben-official-index.md)**

该索引包含：
- ✅ 官方文档完整结构导航（14 个主题）
- ✅ 按使用频率分级的快速入口
- ✅ GitHub 社区资源索引（Issue、Discussions、示例代码）
- ✅ 常见问题速查表
- ✅ 当前项目的配置对照

**优先级提醒**：
| 主题 | 优先级 | 理由 |
|------|:------:|------|
| 路由和菜单 | ⭐⭐⭐ | 动态路由生成、菜单格式是当前最大问题来源 |
| 权限/访问控制 | ⭐⭐⭐ | 后端模式 `accessMode: backend` 是本项目核心 |
| 服务端交互 | ⭐⭐⭐ | API 封装、响应格式、错误拦截直接影响前端功能 |
| 构建与部署 | ⭐⭐⭐ | 环境变量、构建配置、部署方案 |
| Vxe Table | ⭐⭐⭐ | 项目所有列表页面都依赖该组件 |
| 登录 | ⭐⭐ | 登录流程、API 要求（若需修改时查阅） |
| 配置 | ⭐⭐ | 应用设置（若需修改时查阅） |
| 其他 | ⭐ | 按需查阅 | |

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

## 三、当前页面合规分析（2026-07-02 更新）

| 文件 | 合规状态 | 说明 |
|------|:-------:|------|
| `ui/src/api/contracts.ts` | ✅ 合规 | 使用 `requestClient` |
| `ui/src/api/invoices.ts` | ✅ 合规 | 使用 `requestClient` |
| `ui/src/api/suppliers.ts` | ✅ 合规 | 使用 `requestClient` |
| `ui/src/views/contracts/index.vue` | ✅ 合规 | 使用 `useVbenVxeGrid` |
| `ui/src/views/contracts/detail.vue` | ⚠️ 基本合规 | 使用 Vben 页面布局，可进一步优化 |
| `ui/src/views/invoices/index.vue` | ✅ 合规 | 使用 `useVbenVxeGrid` |
| `ui/src/views/suppliers/index.vue` | ✅ 合规 | 使用 `useVbenVxeGrid` |
| 路由文件 (4个) | ✅ 合规 | `path: ''` + `ignoreAccess: true` + `#/` 路径别名 |

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

## 七、Vben 框架铁律（2026-07-02 强制执行）

> **本项目的 Vben 框架开发、维护、配置、发布、调试——所有相关活动，必须先查阅官方文档再动手。** 这是不可违反的底线。

### 7.1 适用范围

本铁律覆盖所有与 Vben 框架相关的活动：

| 活动类型 | 包含内容 | 必须参考文档 |
|---------|---------|------------|
| **开发** | 路由配置、菜单生成、页面组件、API 封装、表单/表格 | 对应官方文档章节 |
| **修改** | 框架源码修改、现有页面改版、组件替换 | 权限/路由/组件文档 |
| **配置** | 环境变量、偏好设置、权限模式、构建配置 | 配置/开发/部署文档 |
| **发布/部署** | 构建优化、Nginx 配置、CDN 部署、环境切换 | 构建与部署文档 |
| **后端接入** | `get-permission-info` 格式、菜单数据结构、API 响应格式 | 权限/服务端交互文档 |
| **调试排错** | 页面空白、API 报错、路由不显示、菜单不见 | 常见问题速查 + 社区 Issue |
| **UI 定制** | 主题、样式覆盖、暗黑模式 | 样式文档 + 品牌定制 |
| **升级迁移** | Vben 版本升级、破坏性变更适配 | 迁移文档 + 仓库 Release Notes |

### 7.2 操作流程（三步强制）

```
步骤 1：查文档
   ├── 打开 docs/vben-official-index.md
   ├── 找到对应主题的官方文档链接
   └── 完整阅读相关章节

步骤 2：改代码
   ├── 严格按文档规范的格式编写
   ├── 可疑/不确定的地方：再去查一次文档
   └── 文档不足时：搜索 GitHub Issues/Discussions

步骤 3：验证
   ├── curl 验证 API 响应格式
   ├── 浏览器清缓存后测试
   └── 确认 Console 无报错
```

### 7.3 后端接入规范（官方认证）

`accessMode: 'backend'` 模式下，`get-permission-info` 返回的菜单数据格式：

```typescript
// 官方规范：https://doc.vben.pro/guide/in-depth/access.html
interface BackendMenu {
  name: string;           // 路由名称（必须唯一）
  path: string;           // 路由路径
  redirect?: string;      // 重定向（可选）
  component?: string;     // 组件路径，去掉 views/ 和 .vue
  meta: {
    title: string;        // 菜单标题
    icon?: string;        // 图标
    order?: number;       // 排序
    [key: string]: any;   // 其他元数据，如 affixTab、keepAlive
  };
  children?: BackendMenu[];
}
```

**注意**：RuoYi-Office-Vben 定制版额外使用 `convertServerMenuToRouteRecordStringComponent()` 做格式转换，需要额外字段见 `packages/utils/src/helpers/generate-menus.ts`。

### 7.4 何时去 GitHub/社区搜索

以下情况，官方文档不足以解决问题时：

| 场景 | 搜索位置 | 搜索方法 |
|------|---------|---------|
| 遇到 Bug | `vue-vben-admin` Issues | `label:bug` + 关键词搜索 |
| 不确定用法 | 官方 Playground 示例 | 查找对应功能的实现代码 |
| 版本兼容问题 | Release Notes + Breaking Changes | 查看版本间的破坏性变更 |
| RuoYi-Office 定制问题 | RuoYi-Office-Vben 仓库 | 查看其与原生 Vben 的差异 |
| 最佳实践 | Discussions / Stack Overflow | 搜索 "Vben Admin 5 + 关键词" |

### 7.5 违规记录

| 日期 | 违规内容 | 后果 | 修正措施 |
|------|---------|------|---------|
| 2026-07-02 | 未查官方文档，凭猜测修改 `get-permission-info` 菜单格式 | 菜单重复×2、404 报错、列表无法加载 | 删除硬编码路由文件，按官方规范统一后端数据源 |
| 2026-07-02 | 未查官方文档，凭猜测修改 CORS 配置 | CORS 不合规，潜在跨域问题 | 查阅 MDN CORS 规范后修复 |

---

**遵守原则**：查文档 → 改代码 → 验证，三步缺一不可。不确定的先去查再回来，不要猜。
