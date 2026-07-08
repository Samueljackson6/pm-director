# Vben Admin 5 框架开发规则

> 本文件记录了 pm-director 项目在 Vben Admin 5 框架下的**强制开发规则**。
> 所有在 Vben 框架内的开发、配置、修改、维护工作，必须遵守以下规则。
> 来源：`ui-vben/docs/src/guide/` 官方文档 + 实际项目踩坑总结。

---

## 1. 路由与菜单

### 1.1 路由控制模式

本项目使用 **`accessMode: 'backend'`**（后端路由模式）。这意味着：

- **路由不是由前端 `src/router/routes/modules/` 文件控制**，而是由**后端 API `/system/auth/get-permission-info` 返回的菜单数据**控制。
- 前端 `modules/` 下的文件是**兜底路由**，仅在后端菜单 API 无数据时的 fallback。
- 后端返回的 `menus` 数据结构中，`component` 字段指向 `views/` 下的路径，**去掉 `views/` 前缀和 `.vue` 后缀**（如 `/dashboard/overview/index` 对应 `views/dashboard/overview/index.vue`）。

### 1.2 新增页面的步骤

1. **在 `views/` 下创建页面组件**，路径对应后端菜单的 `component` 字段
2. **在后端 `backend/routers/auth.py` 的 `vben_permission_info()` 函数的 `menus` 列表中添加菜单项**
3. 菜单项必须包含：`id`, `parentId`, `name`, `path`, `component`, `componentName`, `icon`, `visible`, `keepAlive`, `sort`

### 1.3 菜单数据结构

```json
{
  "id": 1,
  "parentId": 0,
  "name": "概览",
  "path": "/dashboard",
  "component": "BasicLayout",
  "componentName": "Dashboard",
  "icon": "lucide:layout-dashboard",
  "visible": true,
  "keepAlive": false,
  "sort": 0,
  "children": [
    {
      "id": 11,
      "parentId": 1,
      "name": "综合看板",
      "path": "overview/index",
      "component": "/dashboard/overview/index",
      "componentName": "DashboardOverview",
      "icon": "",
      "visible": true,
      "keepAlive": false,
      "sort": 1
    }
  ]
}
```

### 1.4 路由 Meta 配置

常用配置项（参考官方文档）：

| 属性 | 类型 | 说明 |
|------|------|------|
| `title` | string | 页面标题，显示在菜单和标签页 |
| `icon` | string | 图标名称或URL |
| `order` | number | 菜单排序，仅对一级菜单有效 |
| `ignoreAccess` | boolean | 忽略权限，直接可访问 |
| `hideInMenu` | boolean | 菜单中隐藏 |
| `keepAlive` | boolean | 开启KeepAlive缓存 |
| `affixTab` | boolean | 固定标签页不可关闭 |
| `authority` | string[] | 需要特定角色才可访问 |

### 1.5 默认首页

登录后跳转的默认首页由以下优先级决定（见 `src/router/guard.ts`）：

1. URL 参数 `redirect`
2. **后端 API 返回的 `homePath`**（`backend/routers/auth.py` 中的 `user.homePath` 字段）
3. `findFirstMenuPath(accessMenus)` 第一个可访问菜单
4. `preferences.app.defaultHomePath`（`preferences.ts` 配置，末尾兜底）

---

## 2. 组件与导入

### 2.1 VxeTable 表格组件

❌ **错误用法**（直接使用 slot 解构 `{ row }`）：
```vue
<VxeColumn field="amount" title="金额(万元)">
  <template #default="{ row }">
    {{ row.amount }}
  </template>
</VxeColumn>
```

✅ **正确用法**（从 adapter 导入，使用 `:formatter`）：
```vue
<script setup>
import { VxeTable, VxeColumn } from '#/adapter/vxe-table';
</script>

<VxeTable :data="data" ...>
  <VxeColumn field="amount" title="金额(万元)"
    :formatter="({ cellValue }) => cellValue != null ? Number(cellValue).toFixed(2) : '-'"
  />
</VxeTable>
```

### 2.2 ECharts 图表

必须使用 `@vben/plugins/echarts` 提供的 `EchartsUI` 组件和 `useEcharts` hook：

```vue
<script setup>
import type { EchartsUIType } from '@vben/plugins/echarts';
import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

function buildOption() { return { /* ECharts option */ }; }
onMounted(() => renderEcharts(buildOption()));
watch(() => props.data, () => renderEcharts(buildOption()), { deep: true });
</script>

<template>
  <EchartsUI ref="chartRef" />
</template>
```

### 2.3 API 请求

使用统一的 `requestClient`（`#/api/request`），已配置自动解包 `data` 字段：

```ts
import { requestClient } from '#/api/request';

export function getDashboardOverviewApi() {
  return requestClient.get<DashboardOverview>('/api/dashboard/overview');
}
```

---

## 3. 目录结构

```
src/
  api/           # API 接口封装
  views/         # 页面组件（路由组件路径映射自 views/）
  router/
    routes/
      modules/   # 路由模块文件（仅作为后端菜单兜底）
      core/      # 核心路由（登录/404等，不改）
  components/    # 公共组件
  layouts/       # 布局组件
  store/         # 状态管理
  adapter/       # 适配层（vxe-table等）
  preferences.ts # 项目配置
```

**新增页面必须**：
1. 将 `.vue` 文件放在 `views/` 下对应目录
2. 在后端 API 的 `menus` 中添加菜单项
3. `component` 字段格式：`/视图路径（去掉views/和.vue后缀）` 如 `/dashboard/overview/index`

---

## 4. 权限控制

本项目使用后端访问控制模式（`accessMode: 'backend'`），权限通过后端 API 返回的菜单数据控制。前端通过 `meta.authority` 配置角色权限。

**菜单可见但禁止访问**：设置 `menuVisibleWithForbidden: true`。

---

## 5. 开发构建

### 5.1 本地构建
```bash
# 构建 web-antd 应用（pm-director 主前端）
cd ui-vben/apps/web-antd && pnpm build
```

### 5.2 Docker 部署
```bash
# 后端修改后必须重建镜像（源码不挂载，只挂载 database/ 和 cache/）
docker compose build backend && docker compose up -d backend

# 前端修改后只需重建 dist（容器挂载宿主 dist 目录）
cd ui-vben/apps/web-antd && pnpm build
# 然后刷新浏览器（或硬刷新 Ctrl+Shift+R）
```

### 5.3 测试
```bash
# vitest 单元测试（在 web-antd 目录下执行）
pnpm vitest run

# playwright 功能验证（在 .devtest/ 下执行）
cd .devtest && node playwright-t9.mjs
```

---

## 6. 项目特有规则

### 6.1 后端 Mock Auth
- 所有菜单数据硬编码在 `backend/routers/auth.py` 的 `vben_permission_info()` 中
- 默认登录账号：admin / admin123
- 响应统一用 `vben_response()` 包装为 `{ code:0, data, message:"success" }`

### 6.2 金额单位
- 所有金额统一使用 **万元**
- overview 端点返回 `currency_unit: "万元"`，前端据此展示

### 6.3 常见错误及解决

| 症状 | 原因 | 解决 |
|------|------|------|
| 新增路由 404 | 后端菜单 API 未添加菜单项 | 在 `auth.py` 的 `menus` 中添加对应项 |
| 页面白屏 bodyLen≈56 | VxeTable slot 解构错误 | 改用 `#/adapter/vxe-table` 的 `:formatter` |
| 侧边栏无新菜单 | 后端菜单 API 未返回 | 检查 `get-permission-info` 响应 |
| login 后跳转不对 | `homePath` 未设或顺序不对 | 修改 `auth.py` 的 `user.homePath` |
| pnpm build 超时 | tail -30 管道阻塞 | 不要用 `| tail -n` 截断 build 输出 |
| 修改 backend 后不生效 | 后端是镜像构建，源码不挂载 | `docker compose build backend` + restart |

---

## 7. 禁止行为

- ❌ **禁止**在前端 `modules/` 中直接添加独立路由绕过后端菜单控制
- ❌ **禁止**修改 `src/router/routes/core/` 核心路由
- ❌ **禁止**直接使用 `vxe-table` 原生的 `VxeTable` slot 解构（`#default="{ row }"`）
- ❌ **禁止**修改 `preferences.ts` 的 `accessMode` 从 `'backend'` 切到其他模式
- ❌ **禁止**把视图文件直接放在 `views/dashboard/` 根目录下（会被 Vben 自动发现覆盖）
- ❌ **禁止**跳过 `docker compose build backend` 直接重启容器（源码在镜像内，不在卷上）
