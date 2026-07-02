# Vben Admin 5 官方文档本地索引

> **版本**: 5.7.0 | **更新日期**: 2026-07-02
> **官方站点**: https://doc.vben.pro/
> **英文版**: https://doc.vben.pro/en/
> **使用规则**: 所有 Vben 框架相关开发/维护/配置/部署，**必须先查阅本文档找到对应章节，阅读官方说明后再动手**。
> **总计**: 44 个文档页面 | 6 大章节 | 13 个组件

---

## 一、文档总览

```
📖 简介 (Introduction)      · 5 篇     🧠 深入 (In-depth)        · 8 篇
🔧 基础 (Essentials)       · 9 篇     🏗️ 工程 (Project)         · 7 篇
🧩 组件 (Components)       · 13 篇    📎 其他 (Other)           · 3 篇
```

---

## 二、快速导航（按使用频率）

| 频率 | 主题 | 官方链接 | 优先级理由 |
|:----:|------|---------|-----------|
| ⭐⭐⭐ | **路由和菜单** | [/guide/essentials/route.html](https://doc.vben.pro/guide/essentials/route.html) | 路由meta配置(22+项)、动态路由生成、菜单控制——本项目频发问题来源 |
| ⭐⭐⭐ | **权限/访问控制** | [/guide/in-depth/access.html](https://doc.vben.pro/guide/in-depth/access.html) | 后端模式核心：`fetchMenuListAsync`、权限码、按钮级控制 |
| ⭐⭐⭐ | **服务端交互** | [/guide/essentials/server.html](https://doc.vben.pro/guide/essentials/server.html) | API封装、拦截器、错误处理、Token刷新——后端对接必读 |
| ⭐⭐⭐ | **配置/偏好设置** | [/guide/essentials/settings.html](https://doc.vben.pro/guide/essentials/settings.html) | 13大类100+配置项，`accessMode`、主题、布局等核心配置 |
| ⭐⭐⭐ | **登录** | [/guide/in-depth/login.html](https://doc.vben.pro/guide/in-depth/login.html) | 登录流程、API要求、过期处理 |
| ⭐⭐⭐ | **Vxe Table 表格** | [/components/common-ui/vben-vxe-table.html](https://doc.vben.pro/components/common-ui/vben-vxe-table.html) | 本项目所有列表页核心组件 |
| ⭐⭐ | **构建与部署** | [/guide/essentials/build.html](https://doc.vben.pro/guide/essentials/build.html) | 环境区分、Nginx配置 |
| ⭐⭐ | **Vben Form 表单** | [/components/common-ui/vben-form.html](https://doc.vben.pro/components/common-ui/vben-form.html) | CRUD 表单核心 |
| ⭐⭐ | **Vben Modal / Drawer** | [/components/common-ui/vben-modal.html](https://doc.vben.pro/components/common-ui/vben-modal.html) | 弹窗/抽屉 —— CRUD 必用 |
| ⭐⭐ | **目录结构** | [/guide/project/dir.html](https://doc.vben.pro/guide/project/dir.html) | Monorepo 结构，明确文件位置 |
| ⭐⭐ | **本地开发** | [/guide/essentials/development.html](https://doc.vben.pro/guide/essentials/development.html) | `.env`配置、代理 |
| ⭐⭐ | **样式** | [/guide/essentials/styles.html](https://doc.vben.pro/guide/essentials/styles.html) | Tailwind + CSS Variables |
| ⭐ | **图标** | [/guide/essentials/icons.html](https://doc.vben.pro/guide/essentials/icons.html) | Iconify + 本地SVG |
| ⭐ | **国际化** | [/guide/in-depth/locale.html](https://doc.vben.pro/guide/in-depth/locale.html) | 多语言配置 |
| ⭐ | **常见问题** | [/guide/other/faq.html](https://doc.vben.pro/guide/other/faq.html) | 排错入口 |

---

## 三、完整文档结构（44 篇）

### 3.1 📖 简介（Introduction）

| # | 页面 | 链接 | 说明 | 优先级 |
|:-:|------|------|------|:------:|
| 1 | 关于 Vben Admin | [/guide/introduction/vben.html](https://doc.vben.pro/guide/introduction/vben.html) | 框架定位、特点：国际化/权限/多主题/动态菜单/Monorepo/多UI库 | ⭐⭐⭐ |
| 2 | 为什么选择我们？ | [/guide/introduction/why.html](https://doc.vben.pro/guide/introduction/why.html) | 技术选型分析、对比其他方案 | ⭐⭐ |
| 3 | **快速开始** | [/guide/introduction/quick-start.html](https://doc.vben.pro/guide/introduction/quick-start.html) | Node 22.18+ → pnpm install → pnpm dev | ⭐⭐⭐ |
| 4 | 精简版本 | [/guide/introduction/thin.html](https://doc.vben.pro/guide/introduction/thin.html) | 完整版 vs 精简版 | ⭐ |
| 5 | 组件文档入口 | [/components/introduction.html](https://doc.vben.pro/components/introduction.html) | 组件体系总览 | ⭐⭐⭐ |

### 3.2 🔧 基础（Essentials）

| # | 页面 | 链接 | 说明 | 优先级 |
|:-:|------|------|------|:------:|
| 6 | **基础概念** | [/guide/essentials/concept.html](https://doc.vben.pro/guide/essentials/concept.html) | 包名约定、应用架构、模块划分 | ⭐⭐⭐ |
| 7 | **本地开发** | [/guide/essentials/development.html](https://doc.vben.pro/guide/essentials/development.html) | dev server、HMR、代理配置、`.env`文件 | ⭐⭐⭐ |
| 8 | **路由和菜单** ⭐ | [/guide/essentials/route.html](https://doc.vben.pro/guide/essentials/route.html) | 路由类型/定义/meta(22+项)/新增页面/标签页控制 | ⭐⭐⭐⭐⭐ |
| 9 | **配置** ⭐ | [/guide/essentials/settings.html](https://doc.vben.pro/guide/essentials/settings.html) | 偏好设置(13大类100+项)、环境变量、应用配置 | ⭐⭐⭐⭐⭐ |
| 10 | **图标** | [/guide/essentials/icons.html](https://doc.vben.pro/guide/essentials/icons.html) | Iconify、本地SVG、图标选择器 | ⭐⭐ |
| 11 | **样式** | [/guide/essentials/styles.html](https://doc.vben.pro/guide/essentials/styles.html) | Tailwind + CSS Variables、全局覆盖、组件隔离 | ⭐⭐⭐ |
| 12 | 外部模块 | [/guide/essentials/external-module.html](https://doc.vben.pro/guide/essentials/external-module.html) | 第三方库集成 | ⭐ |
| 13 | **构建与部署** | [/guide/essentials/build.html](https://doc.vben.pro/guide/essentials/build.html) | 生产构建、环境区分、Nginx部署 | ⭐⭐⭐ |
| 14 | **服务端交互** ⭐ | [/guide/essentials/server.html](https://doc.vben.pro/guide/essentials/server.html) | Mock服务、请求客户端、拦截器、Token刷新、跨域 | ⭐⭐⭐⭐⭐ |

### 3.3 🧠 深入（In-depth）

| # | 页面 | 链接 | 说明 | 优先级 |
|:-:|------|------|------|:------:|
| 15 | **登录** ⭐ | [/guide/in-depth/login.html](https://doc.vben.pro/guide/in-depth/login.html) | 登录流程、API要求、过期处理、验证码 | ⭐⭐⭐⭐⭐ |
| 16 | 主题 | [/guide/in-depth/theme.html](https://doc.vben.pro/guide/in-depth/theme.html) | shadcn-vue主题、16种内置、黑暗/色弱模式 | ⭐⭐ |
| 17 | **权限** ⭐ | [/guide/in-depth/access.html](https://doc.vben.pro/guide/in-depth/access.html) | 前端/后端/混合三种模式、按钮级权限码 | ⭐⭐⭐⭐⭐ |
| 18 | 国际化 | [/guide/in-depth/locale.html](https://doc.vben.pro/guide/in-depth/locale.html) | Vue I18n、多语言 | ⭐ |
| 19 | 常用功能 | [/guide/in-depth/features.html](https://doc.vben.pro/guide/in-depth/features.html) | 登录过期模式、动态标题、水印 | ⭐⭐ |
| 20 | 检查更新 | [/guide/in-depth/check-updates.html](https://doc.vben.pro/guide/in-depth/check-updates.html) | 前端版本检测 | ⭐ |
| 21 | 全局Loading | [/guide/in-depth/loading.html](https://doc.vben.pro/guide/in-depth/loading.html) | 页面加载状态控制 | ⭐ |
| 22 | 组件库切换 | [/guide/in-depth/ui-framework.html](https://doc.vben.pro/guide/in-depth/ui-framework.html) | AntDV/Naive/Element Plus/TDesign切换 | ⭐ |

### 3.4 🏗️ 工程（Project）

| # | 页面 | 链接 | 说明 | 优先级 |
|:-:|------|------|------|:------:|
| 23 | 规范 | [/guide/project/standard.html](https://doc.vben.pro/guide/project/standard.html) | 命名、Git提交、ESLint规范 | ⭐⭐ |
| 24 | CLI | [/guide/project/cli.html](https://doc.vben.pro/guide/project/cli.html) | vsh工具：创建页面、生成模块 | ⭐⭐ |
| 25 | **目录说明** | [/guide/project/dir.html](https://doc.vben.pro/guide/project/dir.html) | Monorepo目录：6个apps、20+packages | ⭐⭐⭐ |
| 26 | 单元测试 | [/guide/project/test.html](https://doc.vben.pro/guide/project/test.html) | Vitest | ⭐ |
| 27 | Tailwind CSS | [/guide/project/tailwindcss.html](https://doc.vben.pro/guide/project/tailwindcss.html) | Tailwind v4配置 | ⭐⭐ |
| 28 | Changeset | [/guide/project/changeset.html](https://doc.vben.pro/guide/project/changeset.html) | 版本管理/Changelog | ⭐ |
| 29 | Vite Config | [/guide/project/vite.html](https://doc.vben.pro/guide/project/vite.html) | Vite配置详解、构建优化 | ⭐⭐ |

### 3.5 📎 其他（Other）

| # | 页面 | 链接 | 说明 | 优先级 |
|:-:|------|------|------|:------:|
| 30 | 项目更新 | [/guide/other/project-update.html](https://doc.vben.pro/guide/other/project-update.html) | 旧版升级到v5 | ⭐ |
| 31 | 移除代码 | [/guide/other/remove-code.html](https://doc.vben.pro/guide/other/remove-code.html) | 移除不需要的模块 | ⭐ |
| 32 | **常见问题** | [/guide/other/faq.html](https://doc.vben.pro/guide/other/faq.html) | 依赖/缓存/页面空白/打包/Node版本/Nginx | ⭐⭐⭐ |

### 3.6 🧩 组件（Components）

| # | 组件 | 链接 | 说明 | 优先级 |
|:-:|------|------|------|:------:|
| 33 | Page 页面 | [/components/layout-ui/page.html](https://doc.vben.pro/components/layout-ui/page.html) | 页面顶层容器 | ⭐⭐⭐ |
| 34 | Vben Api Component | [/components/common-ui/vben-api-component.html](https://doc.vben.pro/components/common-ui/vben-api-component.html) | API数据驱动包装器 | ⭐⭐ |
| 35 | Vben Alert | [/components/common-ui/vben-alert.html](https://doc.vben.pro/components/common-ui/vben-alert.html) | 提示框 | ⭐ |
| 36 | **Vben Modal** | [/components/common-ui/vben-modal.html](https://doc.vben.pro/components/common-ui/vben-modal.html) | 模态框 | ⭐⭐⭐ |
| 37 | **Vben Drawer** | [/components/common-ui/vben-drawer.html](https://doc.vben.pro/components/common-ui/vben-drawer.html) | 抽屉 | ⭐⭐⭐ |
| 38 | **Vben Form** | [/components/common-ui/vben-form.html](https://doc.vben.pro/components/common-ui/vben-form.html) | Schema驱动表单 | ⭐⭐⭐ |
| 39 | **Vben Vxe Table** | [/components/common-ui/vben-vxe-table.html](https://doc.vben.pro/components/common-ui/vben-vxe-table.html) | 表格（vxe-table封装） | ⭐⭐⭐⭐⭐ |
| 40 | Vben CountTo | [/components/common-ui/vben-count-to-animator.html](https://doc.vben.pro/components/common-ui/vben-count-to-animator.html) | 数字动画 | ⭐ |
| 41 | Vben Ellipsis Text | [/components/common-ui/vben-ellipsis-text.html](https://doc.vben.pro/components/common-ui/vben-ellipsis-text.html) | 文本省略 | ⭐⭐ |
| 42 | Vben Descriptions | [/components/common-ui/vben-descriptions.html](https://doc.vben.pro/components/common-ui/vben-descriptions.html) | 描述列表 | ⭐⭐⭐ |
| 43 | **Vben Table Action** | [/components/common-ui/vben-table-action.html](https://doc.vben.pro/components/common-ui/vben-table-action.html) | 表格操作列 | ⭐⭐⭐ |
| 44 | Vben Cropper | [/components/common-ui/vben-cropper.html](https://doc.vben.pro/components/common-ui/vben-cropper.html) | 图片裁剪 | ⭐ |
| 45 | Vben Tiptap | [/components/common-ui/vben-tiptap.html](https://doc.vben.pro/components/common-ui/vben-tiptap.html) | 富文本编辑器 | ⭐⭐ |

---

## 四、本项目的配置对照

| 配置项 | 官方范围 | 当前项目值 | 说明 |
|--------|---------|:----------:|------|
| `app.accessMode` | `frontend`/`backend`/`mixed` | `backend` | 后端控制权限和菜单 |
| `app.defaultHomePath` | 任意路由 | `/dashboard` | 登录后首页 |
| `VITE_GLOB_API_URL` | URL | `http://192.168.0.236:8800` | API 接口地址 |
| `VITE_ROUTER_HISTORY` | `hash`/`history` | `hash` | Hash 模式 |
| `VITE_APP_CAPTCHA_ENABLE` | `true`/`false` | `false` | 验证码已关闭 |
| `VITE_APP_TENANT_ENABLE` | `true`/`false` | `false` | 租户已关闭 |
| `allow_credentials` | CORS | 已关闭 | 移除以防止与 `allow_origins=['*']` 冲突 |

---

## 五、GitHub 官方仓库 & 社区资源

当官方文档不足时：

| 资源 | 地址 | 适用场景 |
|------|------|---------|
| Vben 官方仓库 | https://github.com/vbenjs/vue-vben-admin | 源码、Issue搜索、PR参考 |
| 官方 Playground | https://github.com/vbenjs/vue-vben-admin/tree/main/playground | 功能演示代码 |
| 官方 Issues | https://github.com/vbenjs/vue-vben-admin/issues | Bug搜索、社区解决方案 |
| 官方 Discussions | https://github.com/vbenjs/vue-vben-admin/discussions | 最佳实践、使用问答 |
| RuoYi-Office-Vben | https://gitee.com/yudaocode/yudao-ui-admin-vben | 项目基底框架源码 |
| RuoYi-Vue-Pro | https://github.com/YunaiV/ruoyi-vue-pro | 后端Java API格式参考 |

---

## 六、常见问题速查

| 问题 | 参考文档 | 关键提醒 |
|------|---------|---------|
| 菜单不显示 | 权限→后端模式 | `visible: true`，`hideInMenu` 未设置 |
| 路由不生效 | 路由→动态路由 | `name` 唯一、`component` 路径正确 |
| 路由重复 | 权限→路由生成 | 检查硬编码路由和动态路由的 `name` 冲突 |
| API 报错 | 服务端交互→错误处理 | `{code, data, message}` 格式 |
| 登录失败 | 登录→API要求 | 返回需包含 `accessToken` |
| 登录后 404 | 路由→路由模式 | Hash 模式下 `homePath` 需加 `#/` 前缀 |
| 表格无数据 | Vxe Table→代理配置 | `proxyConfig.ajax.query` 返回 `{items, total}` |
| 构建失败 | 构建与部署 | Node版本 22.18+、pnpm版本 |
| 部署后白屏 | 构建与部署→Nginx | Hash模式不需要特殊配置 |
| 验证码总是弹出 | 登录文档 | 设置 `VITE_APP_CAPTCHA_ENABLE=false` |

---

*本索引对应 Vben Admin 5.7.0。RuoYi-Office-Vben（yudao-ui-admin-vben）定制版可能有差异，以官方文档为准，差异处结合源码分析。*
