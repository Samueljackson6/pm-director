# ADR-001: 使用后端路由模式

日期：2026-07-13
状态：已采纳
决策者：系统审计 + 阶段1实施

---

## 背景

pm-director 项目使用 Vben Admin 5 框架，框架支持两种路由模式：

1. **frontend** - 前端静态路由
2. **backend** - 后端动态路由

项目声明使用 `accessMode: 'backend'`，但实际实现中 `generate-routes-backend.ts` 会无条件合并静态路由，导致：

- 菜单不可见不等于路由不可达
- 同一路由名称可能对应两个路径
- 权限控制无法证明完整

---

## 决策

**采用真正的后端路由模式**：

1. `auth.py` 的菜单定义是路由唯一真值
2. 前端 `routes/modules/` 仅保留 `Legacy*` 重定向
3. 新增页面必须在 `auth.py` 中定义

---

## 理由

### 优点

- **权限可控**：后端菜单控制哪些路由可访问
- **职责清晰**：路由定义集中在一处
- **易于维护**：避免静态和动态路由冲突

### 缺点

- 前端开发需要同步修改后端代码
- 路由变更需要重新构建后端镜像

---

## 实施

### 代码变更

```typescript
// ui-vben/apps/web-antd/src/router/routes/index.ts
const legacyRedirectRoutes = dynamicRoutes.filter(
  (route) => route.name?.toString().startsWith('Legacy'),
);
const accessRoutes = [...legacyRedirectRoutes];
```

### 禁止行为

- 禁止在 `routes/modules/` 中添加业务路由
- 禁止绕过 `auth.py` 直接定义路由

---

## 影响

- 所有新页面必须在 `auth.py` 中定义
- 旧路由逐步迁移到新路由
- 前端开发者需要了解后端代码

---

## 参考

- `docs/vben-framework-rules.md` - Vben 框架规则
- `docs/audits/系统全量审计与改造基线-2026-07-13.md` - 审计报告
