# 返回契约模式

> 本文档记录详情页返回逻辑的规范模式。

---

## 1. 问题背景

### 1.1 审计发现的问题

| 详情页 | 原返回目标 | 问题 |
|--------|-----------|------|
| 项目详情 | ProjectList | 返回隐藏的旧页面 |
| 客户发票详情 | InvoiceList | 返回旧发票页 |
| 供应商详情 | SupplierList | 路径解析错误 |

### 1.2 根因

- 页面没有统一"来源与返回契约"
- 旧路由仍在运行时存在
- 固定跳列表，不保留来源信息

---

## 2. 返回契约原则

### 2.1 三层优先级

```
┌─────────────────────────────────────────────────────────────┐
│                    返回优先级                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 来源优先（最优）                                         │
│     └─ 用户从 A 页面进入详情 → 返回 A 页面                   │
│     └─ 保留筛选、分页、滚动位置                              │
│                                                             │
│  2. 规范兜底（次优）                                         │
│     └─ 无来源信息 → 返回模块规范列表                         │
│     └─ 不保留筛选状态                                        │
│                                                             │
│  3. 旧路由隔离（最后）                                       │
│     └─ 旧路由只做重定向                                      │
│     └─ 新页面不主动跳回旧路由                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 实现模式

### 3.1 推荐写法

```typescript
import { useRouter } from 'vue-router';

const router = useRouter();

// 列表页：进入详情时携带来源
function goToDetail(id: string) {
  router.push({
    name: 'CustomerInvoiceDetail',
    query: { id },
    state: { from: 'CustomerInvoices' }
  });
}

// 详情页：返回逻辑
function goBack() {
  // 优先返回来源
  if (router.options.history.state.back) {
    router.back();
  } else {
    // 兜底：回到规范列表
    router.push({ name: 'CustomerInvoices' });
  }
}
```

### 3.2 禁止写法

```typescript
// 禁止：固定跳旧列表
function goBack() {
  router.push({ name: 'InvoiceList' }); // 旧路由
}

// 禁止：硬编码路径
function goBack() {
  router.push('/invoices'); // 硬编码
}
```

---

## 4. 规范路由名对照表

| 模块 | 列表路由名 | 详情路由名 |
|------|-----------|-----------|
| 合同 | ContractList | ContractDetail |
| 客户发票 | CustomerInvoices | CustomerInvoiceDetail |
| 客户回款 | CustomerReceipts | CustomerReceiptDetail |
| 供应商 | SupplierList | SupplierDetail |
| 供应商发票 | SupplierInvoices | SupplierInvoiceDetail |
| 供应商付款 | SupplierPayments | SupplierPaymentDetail |

---

## 5. 验收标准

- [ ] 详情页返回使用规范路由名
- [ ] 列表页进入详情携带来源
- [ ] 无来源时能正确兜底
- [ ] 不使用旧路由名
