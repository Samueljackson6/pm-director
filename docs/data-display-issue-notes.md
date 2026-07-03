# PM-Director 数据不显示问题分析笔记

> 2026-07-02 | 待明天处理

---

## 一、数据源状态 ✅

| 数据 | 数量 | 字段数 | 数据内容 |
|------|:----:|:------:|---------|
| Contracts | 30 条 | 17 字段 | 合同编号、项目名称、金额、甲方、乙方、签订日期、阶段、付款、交付物 |
| Invoices | 大量 | 18 字段 | 开票/回款记录、金额、税率、状态 |
| Suppliers | 24 条 | 18 字段 | 供应商名称、合同总额、已开票、已付款、状态 |

## 二、API 返回格式 ✅

后端标准响应：
```
HTTP 200 → {"code":0, "data":{items:[...], total:30, page:1, size:20}, "message":"success"}
```

## 三、VxeTable 数据消费链路

```
后端 API →  {code, data: {items, total}} 
  ↓
requestClient 解包 →  {items, total}
  ↓
proxyConfig.ajax.query →  {items: data.items, total: data.total}
  ↓
proxyConfig.response 映射 (result:'items', total:'total')  →  字段名一致
  ↓
VxeGrid 渲染表格
```

数据提交流程**理论上正确**，但页面不显示。

## 四、需要 F12 控制台确认（明天）

1. `requestClient` 实际返回的数据形状（network tab 看请求/响应）
2. 有没有 JavaScript 报错（console tab）
3. VxeGrid 组件是否正常初始化（elements tab 看 DOM）

## 五、RuoYi Office 设计参考

RuoYi 的 CRM 合同管理已完整实现，核心数据模型：

| 表 | 用途 | 关键字段 |
|----|------|---------|
| `crm_contract` | 合同主表 | id, name, no, customer_id, total_price(元), sign_contact_id |
| `crm_receivable` | 回款记录 | id, no, plan_id, contract_id, price, return_time |
| `crm_receivable_plan` | 回款计划 | id, period, contract_id, price, return_time, remind_days |
| `erp_account` | 结算账户 | id, name, no, status |
| `erp_finance_receipt` | 收款单 | id, no, customer_id, account_id, receipt_price |
| `erp_finance_payment` | 付款单 | id, no, supplier_id, account_id, payment_price |

**设计差异**：RuoYi 以客户→商机→合同→回款为线索，金额单位是元；我们以项目为线索，金额单位是万元。

## 六、明天工作计划

1. 开浏览器 F12 → 看 Network + Console
2. 根据报错查 Vben VxeTable 官方文档
3. 修复数据渲染问题
4. 参考 RuoYi 设计，讨论页面和数据是否需要重新设计
