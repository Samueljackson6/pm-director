# Vben Admin 5 官方文档本地索引

> **版本**: 5.7.0 | **更新时间**: 2026-07-02
> **官方站点**: https://doc.vben.pro/
> **使用规则**: 所有 Vben 框架相关开发/维护/配置，**必须先查阅本文档索引找到对应章节，阅读官方说明后再动手**。

---

## 一、快速导航（按使用频率）

| 频率 | 主题 | 链接 | 覆盖内容 |
|:----:|------|------|---------|
| ⭐⭐⭐ | **路由和菜单** | [doc.vben.pro/guide/essentials/route.html](https://doc.vben.pro/guide/essentials/route.html) | 路由配置、菜单生成、动态路由、参数传递 |
| ⭐⭐⭐ | **权限/访问控制** | [doc.vben.pro/guide/in-depth/access.html](https://doc.vben.pro/guide/in-depth/access.html) | 后端模式、前端模式、混合模式、权限码、菜单数据格式 |
| ⭐⭐⭐ | **服务端交互** | [doc.vben.pro/guide/essentials/server.html](https://doc.vben.pro/guide/essentials/server.html) | API 封装、请求拦截、响应处理、错误处理 |
| ⭐⭐⭐ | **构建与部署** | [doc.vben.pro/guide/essentials/build.html](https://doc.vben.pro/guide/essentials/build.html) | 构建配置、环境变量、部署方案、Nginx 配置 |
| ⭐⭐⭐ | **Vxe Table 表格** | [doc.vben.pro/components/common-ui/vben-vxe-table.html](https://doc.vben.pro/components/common-ui/vben-vxe-table.html) | 表格使用、代理配置、分页、编辑、工具栏 |
| ⭐⭐ | **登录页面** | [doc.vben.pro/guide/in-depth/login.html](https://doc.vben.pro/guide/in-depth/login.html) | 登录流程、API 要求、验证码、第三方登录 |
| ⭐⭐ | **配置/偏好设置** | [doc.vben.pro/guide/essentials/settings.html](https://doc.vben.pro/guide/essentials/settings.html) | 应用配置、主题、布局、权限模式 |
| ⭐⭐ | **环境变量** | [doc.vben.pro/guide/essentials/development.html](https://doc.vben.pro/guide/essentials/development.html) | `.env` 文件、`VITE_*` 变量、模式切换 |
| ⭐⭐ | **Vben Form 表单** | [doc.vben.pro/components/common-ui/vben-form.html](https://doc.vben.pro/components/common-ui/vben-form.html) | 表单使用、校验、动态表单项 |
| ⭐ | **快速开始** | [doc.vben.pro/guide/introduction/quick-start.html](https://doc.vben.pro/guide/introduction/quick-start.html) | 环境准备、安装、启动 |
| ⭐ | **目录结构** | [doc.vben.pro/guide/project/dir.html](https://doc.vben.pro/guide/project/dir.html) | 项目目录说明 |
| ⭐ | **样式** | [doc.vben.pro/guide/essentials/styles.html](https://doc.vben.pro/guide/essentials/styles.html) | CSS 变量、主题定制 |
| ⭐ | **图标** | [doc.vben.pro/guide/essentials/icons.html](https://doc.vben.pro/guide/essentials/icons.html) | 图标使用、自定义图标 |
| ⭐ | **国际化** | [doc.vben.pro/guide/in-depth/locale.html](https://doc.vben.pro/guide/in-depth/locale.html) | 多语言配置 |
| ⭐ | **本地开发** | [doc.vben.pro/guide/essentials/development.html](https://doc.vben.pro/guide/essentials/development.html) | 开发服务器、代理、HTTPS |

---

## 二、完整文档结构

### 2.1 Guide 指南

| 章节 | 页面 | 说明 |
|------|------|------|
| Introduction | 快速开始 | 环境要求、安装步骤、启动项目 |
| Essentials | 本地开发 | 开发服务器、代理配置、HTTPS 设置 |
| Essentials | 路由和菜单 | 路由配置、动态路由、菜单生成、参数传递、外链 |
| Essentials | 服务端交互 | requestClient、baseRequestClient、拦截器、错误处理 |
| Essentials | 构建与部署 | 构建命令、环境变量、部署方案 |
| Essentials | 配置 | 偏好设置、主题、布局、权限模式配置 |
| Essentials | 样式 | CSS 变量、暗黑模式、主题定制 |
| Essentials | 图标 | 图标集、自定义图标 |
| Essentials | 国际化 | i18n 配置、语言切换 |

### 2.2 In-depth 深入

| 页面 | 说明 | 关键点 |
|------|------|--------|
| **登录** | 登录流程、API 要求 | 登录接口返回 `accessToken`，用户信息接口返回 `roles` |
| **权限** | 三种权限模式详解 | 后端模式：`fetchMenuListAsync` 获取菜单，动态生成路由 |
| 国际化 | 多语言配置 | — |

### 2.3 Components 组件

| 组件 | 说明 | 优先级 |
|------|------|:------:|
| Vben Form 表单 | 表单构建、校验 | ⭐⭐ |
| **Vben Vxe Table 表格** | 表格组件、代理模式、编辑 | ⭐⭐⭐ |
| Vben Modal 模态框 | 弹窗、抽屉 | ⭐ |
| Vben Button 按钮 | 按钮组件 | ⭐ |
| Vben Input 输入框 | 输入框 | ⭐ |
| Vben Select 选择器 | 下拉选择 | ⭐ |
| Vben Card 卡片 | 卡片布局 | ⭐ |
| Vben Description 描述 | 详情展示 | ⭐ |

### 2.4 配置参考

| 配置项 | 说明 | 当前项目值 |
|--------|------|:----------:|
| `app.accessMode` | 权限模式 | `backend` |
| `app.defaultHomePath` | 默认首页 | `/dashboard` |
| `VITE_GLOB_API_URL` | API 基础地址 | `http://192.168.0.236:8800` |
| `VITE_ROUTER_HISTORY` | 路由模式 | `hash` |
| `VITE_APP_CAPTCHA_ENABLE` | 验证码开关 | `false` |

---

## 三、GitHub 官方仓库 & 社区资源

当官方文档不足时（如 Bug、版本差异、RuoYi-Office 定制问题）：

| 资源 | 地址 | 适用场景 |
|------|------|---------|
| Vben 官方 GitHub | https://github.com/vbenjs/vue-vben-admin | 源码阅读、Issue 搜索、PR 参考 |
| Vben 官方示例 | https://github.com/vbenjs/vue-vben-admin/tree/main/playground | 功能演示代码 |
| RuoYi-Office-Vben | https://gitee.com/yudaocode/yudao-ui-admin-vben | 项目基底框架，定制修改参考 |
| RuoYi-Vue-Pro | https://github.com/YunaiV/ruoyi-vue-pro | 后端 Java 源码，API 响应格式参考 |
| Vben Issues | https://github.com/vbenjs/vue-vben-admin/issues | Bug 搜索、社区解决方案 |
| Vben Discussions | https://github.com/vbenjs/vue-vben-admin/discussions | 最佳实践、使用问答 |

---

## 四、常见问题速查

| 问题 | 参考文档 | 关键提醒 |
|------|---------|---------|
| 菜单不显示 | 权限文档 → 后端模式 | 检查 `visible: true`，`hideInMenu` 未设置 |
| 路由不生效 | 路由文档 → 动态路由 | 检查 `name` 唯一性、`component` 路径 |
| API 报错 | 服务端交互文档 → 错误处理 | 检查响应格式 `{code, data, message}` |
| 登录失败 | 登录文档 → API 要求 | 检查返回格式包含 `accessToken` |
| 构建失败 | 构建与部署文档 | 检查 Node 版本、依赖安装 |
| 部署后白屏 | 构建与部署文档 → Nginx 配置 | Hash 模式不需要特殊配置 |
| 表格不显示数据 | Vxe Table 文档 → 代理配置 | 检查 `proxyConfig.ajax.query` 返回格式 |

---

*本索引对应 Vben Admin 5.7.0，RuoYi-Office-Vben 定制版可能有所差异，如有冲突以官方文档为准。*
