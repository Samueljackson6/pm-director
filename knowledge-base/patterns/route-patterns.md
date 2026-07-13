# 路由模式

> 本文档记录 pm-director 项目的路由开发模式。

---

## 1. 后端路由模式

### 1.1 配置

本项目使用 `accessMode: 'backend'`，路由由后端 API 控制。

**配置位置**：`ui-vben/apps/web-antd/src/preferences.ts`

```typescript
app: {
  accessMode: 'backend',
}
```

### 1.2 菜单定义位置

**文件**：`backend/routers/auth.py`

**端点**：`GET /system/auth/get-permission-info`

### 1.3 路由生成流程

```
1. 前端启动
   └─ 调用 /system/auth/get-permission-info

2. 后端返回菜单数据
   └─ menus 数组包含所有路由定义

3. 前端生成路由
   └─ generateRoutesByBackend() 解析菜单数据
   └─ 只保留 Legacy* 重定向（静态路由已禁用）

4. 用户访问
   └─ 动态路由生效
```

---

## 2. 路径格式规范

### 2.1 一级模块

```python
{
    'name': '供应商管理',
    'path': '/suppliers',        # 绝对路径
    'component': 'BasicLayout',
    'componentName': 'Suppliers',
}
```

### 2.2 子菜单

```python
{
    'name': '供应商列表',
    'path': 'list',              # 相对路径！
    'component': '/suppliers/list/index',
    'componentName': 'SupplierList',
}
```

### 2.3 详情页

```python
{
    'name': '供应商详情',
    'path': 'detail',
    'component': '/suppliers/detail/index',
    'componentName': 'SupplierDetail',
    'visible': False,            # 隐藏在菜单中
}
```

---

## 3. 常见问题

### 3.1 404 错误

**原因**：子菜单使用绝对路径

```python
# 错误
'path': '/suppliers'

# 正确
'path': 'list'
```

**结果**：`/suppliers` + `/suppliers` = `/suppliers/suppliers` → 404

### 3.2 组件加载失败

**原因**：组件路径格式错误

```python
# 错误
'component': 'suppliers/list/index.vue'
'component': '/views/suppliers/list/index.vue'

# 正确
'component': '/suppliers/list/index'
```

### 3.3 路由重名

**原因**：不同模块使用相同的 componentName

**解决**：每个路由使用唯一的 componentName

---

## 4. 调试命令

```bash
# 检查后端菜单定义
curl -s http://localhost:18080/system/auth/get-permission-info | python -c "
import sys, json
d = json.load(sys.stdin)
for m in d.get('data', {}).get('menus', []):
    print(f\"{m['name']}: {m['path']}\")
    for c in m.get('children', []):
        print(f\"  - {c['name']}: {c['path']}\")
"

# 检查前端路由
# 在浏览器控制台执行
console.log($router.getRoutes())
```

---

## 5. 相关文档

- `docs/贡献约束.md` - 路由规范
- `docs/规范路由清单-20260713.md` - 规范路由注册表
- `knowledge-base/patterns/return-contract.md` - 返回契约
