# 阶段1完成归档：路由与发布基线修复

日期：2026-07-13
类型：阶段完成
相关：PR #33, Issue #34

---

## 背景

系统全量审计发现四套基础关系同时失控，其中路由和发布是核心问题：

1. **菜单与路由没有唯一真值** — 后端模式被改造成静态与动态路由混合
2. **源码、容器和实际页面版本不一致** — PR 已合并不等于前端已部署

---

## 完成的工作

### 1. 供应商菜单路径修复

**问题**：子菜单使用绝对路径 `/suppliers`，导致路径拼接为 `/suppliers/suppliers` → 404

**修复**：
```python
# backend/routers/auth.py
{
    'name': '供应商列表',
    'path': 'list',  # 改为相对路径
    'component': '/suppliers/list/index',  # 更新组件路径
}
```

### 2. 静态路由清理

**问题**：`generate-routes-backend.ts` 无条件合并静态路由

**修复**：
```typescript
// routes/index.ts
const legacyRedirectRoutes = dynamicRoutes.filter(
  (route) => route.name?.toString().startsWith('Legacy'),
);
const accessRoutes = [...legacyRedirectRoutes];
```

### 3. 返回契约修复

**问题**：客户发票详情返回旧 `InvoiceList`

**修复**：
```typescript
// customer-finance/invoices/detail.vue
function goBack() {
  router.push({ name: 'CustomerInvoices' });
}
```

### 4. 旧路由重定向

**新增**：`routes/modules/legacy-redirects.ts`

| 旧路径 | 新路径 |
|--------|--------|
| /invoices | /customer-finance/invoices |
| /projects | /dashboard/overview/index |

---

## 遗留问题

Issue #34 记录了需要跟进的问题：

- 部分详情页仍使用旧路由名
- 仪表盘组件使用旧路径
- 测试 mock 使用脆弱的字符串匹配

---

## 教训

### 1. 路径格式要规范

- 子菜单必须使用相对路径
- 组件路径格式要统一

### 2. 路由要有唯一真值

- 后端模式就要真正使用后端定义
- 不能混合静态和动态路由

### 3. 版本一致性要验证

- PR 合并 ≠ 用户看到
- 必须重新构建和部署

### 4. 跨文件引用要检查

- 修改路由名后，要搜索所有引用
- Code Review 要包含跨文件检查

---

## 参考

- 审计报告：`docs/audits/系统全量审计与改造基线-2026-07-13.md`
- 路由矩阵：`docs/audits/菜单路由与返回链路矩阵-2026-07-13.md`
- 路由清单：`docs/规范路由清单-20260713.md`
