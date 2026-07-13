# 供应商详情页面 - 企查查 MCP 集成

**功能完成日期**: 2026-07-13
**数据来源**: 企查查 MCP（5个维度低积分查询）

---

## 📋 功能概述

基于企查查 MCP 的优化查询策略，为供应商详情页面提供以下5个维度的企业信息：

1. ✅ **工商信息** (`get_company_registration_info`)
2. ✅ **企业简介** (`get_company_profile`)
3. ✅ **风险扫描** (`get_company_risk_scan`)
4. ✅ **软件著作权** (`get_software_copyright_info`)
5. ✅ **对外投资** (`get_external_investments`)

---

## 💰 积分消耗优化

### 查询策略

| 维度 | 工具名称 | 预计积分 | 说明 |
|------|---------|---------|------|
| 工商信息 | `get_company_registration_info` | ~1 | 企业基本身份识别 |
| 企业简介 | `get_company_profile` | ~1 | 业务定位和行业分类 |
| 风险扫描 | `get_company_risk_scan` | ~2 | 35项风险因子聚合扫描 |
| 软件著作权 | `get_software_copyright_info` | ~1 | 技术实力评估 |
| 对外投资 | `get_external_investments` | ~2 | 投资布局分析 |
| **总计** | **5个接口** | **~7积分** | **优化版查询** |

### 对比全量查询

- **全量查询**: 15+ 接口，~25 积分
- **优化查询**: 5 接口，~7 积分
- **节省**: ~18 积分（节省 72%）

---

## 🏗️ 架构设计

### 前端架构

```
供应商详情页面 (detail.vue)
    ↓
API 接口 (suppliers.ts)
    ↓
后端路由 (routers/suppliers.py)
    ↓
企查查 MCP 客户端 (qcc_mcp_client.py)
    ↓
企查查 MCP 服务器 (agent.qcc.com)
```

### 文件结构

```
D:\Tare-workspace\pm-director\
├── backend/
│   ├── qcc_mcp_client.py          # 企查查 MCP 客户端
│   └── routers/
│       └── suppliers.py            # 供应商路由（已添加企查查端点）
│
└── ui-vben/apps/web-antd/src/
    ├── api/
    │   └── suppliers.ts            # 供应商 API（已添加企查查接口）
    └── views/
        └── supplier/
            └── detail.vue          # 供应商详情页面
```

---

## 🔌 API 接口

### 后端 API

#### 1. 聚合查询（推荐）

```http
GET /api/suppliers/qcc/{credit_code}
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "basic_info": { ... },
    "profile": { ... },
    "risk_scan": { ... },
    "software_copyrights": { ... },
    "external_investments": { ... }
  }
}
```

#### 2. 单独查询

```http
GET /api/suppliers/qcc/{credit_code}/basic        # 工商信息
GET /api/suppliers/qcc/{credit_code}/profile      # 企业简介
GET /api/suppliers/qcc/{credit_code}/risk         # 风险扫描
GET /api/suppliers/qcc/{credit_code}/software     # 软件著作权
GET /api/suppliers/qcc/{credit_code}/investment   # 对外投资
```

### 前端 API

```typescript
// 聚合查询
import { getSupplierQccInfoApi } from '#/api/suppliers'

const data = await getSupplierQccInfoApi(creditCode)

// 单独查询
import {
  getQccBasicApi,
  getQccProfileApi,
  getQccRiskApi,
  getQccSoftwareApi,
  getQccInvestmentApi
} from '#/api/suppliers'
```

---

## 📊 数据结构

### 1. 工商信息 (`basic_info`)

```json
{
  "企业名称": "北京振华永创智能科技有限公司",
  "统一社会信用代码": "91110105353028391H",
  "法定代表人": "刘琼玲",
  "登记状态": "存续（在营、开业、在册）",
  "成立日期": "2015-08-18",
  "注册资本": "1005万元",
  "实缴资本": "1005万元",
  "企业类型": "有限责任公司（自然人投资或控股）",
  "参保人数": "42",
  "注册地址": "北京市丰台区...",
  "经营范围": "技术推广服务；软件开发；..."
}
```

### 2. 企业简介 (`profile`)

```json
{
  "企业名称": "北京振华永创智能科技有限公司",
  "简介": "专注于智慧行业应用的方案提供商...",
  "企查查行业": "通用设备批发"
}
```

### 3. 风险扫描 (`risk_scan`)

```json
{
  "企业名称": "北京振华永创智能科技有限公司",
  "摘要": "已全量扫描 35 项风险因子：0 项有记录、35 项无记录。",
  "有记录因子数": 0,
  "无记录因子数": 35,
  "风险因子扫描": [
    {
      "风险因子": "失信信息",
      "条目数": 0,
      "明细工具": "get_dishonest_info"
    },
    ...
  ]
}
```

### 4. 软件著作权 (`software_copyrights`)

```json
{
  "企业名称": "北京振华永创智能科技有限公司",
  "摘要": "该查询实体共有34条软件著作权记录。",
  "软件著作权信息": [
    {
      "软件全称": "水库四预系统化管理软件",
      "登记号": "2026SR0410101",
      "登记日期": "2026-03-10",
      "权利取得方式": "原始取得"
    },
    ...
  ]
}
```

### 5. 对外投资 (`external_investments`)

```json
{
  "企业名称": "北京振华永创智能科技有限公司",
  "摘要": "该查询实体共有2条对外投资记录。",
  "对外投资信息": [
    {
      "被投资企业名称": "成都振华永创科技有限公司",
      "状态": "存续",
      "成立日期": "2026-02-26",
      "持股比例": "30%",
      "认缴出资额/持股数": "30万元"
    },
    ...
  ]
}
```

---

## 🎨 页面功能

### 页面布局

```
┌─────────────────────────────────────────────────┐
│ 标题栏：供应商详情 · 统一社会信用代码              │
│          状态标签 · 风险评级 · 刷新按钮           │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│ KPI 指标行（5个关键指标）                         │
│ 注册资本 | 成立年限 | 参保人数 | 软著数量 | 对外投资 │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│ 吸顶锚点栏：基本信息 | 风险扫描 | 知识产权 | 投资  │
└─────────────────────────────────────────────────┘
┌───────────────────────────┬─────────────────────┐
│ 工商信息卡片 (8/12)        │ 风险扫描卡片 (4/12)  │
│  - 企业标识                │  - 风险等级         │
│  - 注册信息                │  - 风险统计         │
│  - 企业简介                │  - 风险因子详情      │
│  - 经营范围                │                     │
└───────────────────────────┴─────────────────────┘
┌───────────────────────────┬─────────────────────┐
│ 软件著作权卡片             │ 对外投资卡片         │
│  - 软著列表（前10项）       │  - 投资企业列表      │
│  - 查看全部按钮             │                     │
└───────────────────────────┴─────────────────────┘
┌─────────────────────────────────────────────────┐
│ 综合评级卡片                                     │
│  基本资质 | 风险状况 | 技术实力 | 经营稳定性 | 综合 │
│    ⭐⭐⭐⭐     ⭐⭐⭐⭐⭐    ⭐⭐⭐⭐⭐    ⭐⭐⭐⭐    4.2分  │
└─────────────────────────────────────────────────┘
```

### 核心功能

1. **KPI 指标行**: 快速了解供应商核心指标
2. **吸顶导航**: 快速定位到各个信息区块
3. **风险扫描**: 直观展示风险等级和详细因子
4. **技术实力**: 软件著作权列表展示技术能力
5. **投资布局**: 对外投资展示企业战略布局
6. **综合评级**: 多维度评分，量化供应商资质

---

## 🚀 使用指南

### 前置条件

1. **企查查 API Token**: 已配置在环境变量 `QCC_API_TOKEN`
2. **后端依赖**: `httpx` (异步 HTTP 客户端)
3. **前端路由**: 已配置供应商详情页路由

### 安装依赖

```bash
# 后端
cd backend
pip install httpx

# 前端（已在项目中）
cd ui-vben/apps/web-antd
pnpm install
```

### 启动服务

```bash
# 启动后端
cd backend
uvicorn main:app --reload

# 启动前端
cd ui-vben/apps/web-antd
pnpm dev
```

### 访问页面

```
http://localhost:8900/web/supplier/detail?id=91110105353028391H
```

---

## 🔧 配置说明

### 环境变量

```bash
# .env 文件
QCC_API_TOKEN=MqQRwv2e0N5SLDGYlqmxKVM0NzvsLNot6kTZF50l08N1zih4
```

### 路由配置

需要在路由配置文件中添加供应商详情页路由：

```typescript
{
  path: '/supplier/detail',
  name: 'SupplierDetail',
  component: () => import('#/views/supplier/detail.vue'),
  meta: {
    title: '供应商详情'
  }
}
```

---

## 📈 性能优化

### 并发查询

后端使用 `asyncio.gather()` 并发查询5个维度，显著减少响应时间：

```python
results = await asyncio.gather(
    self.get_company_registration_info(search_key),
    self.get_company_profile(search_key),
    self.get_company_risk_scan(search_key),
    self.get_software_copyright_info(search_key),
    self.get_external_investments(search_key)
)
```

### 缓存策略（推荐）

建议添加 Redis 缓存，缓存策略：

| 数据类型 | 缓存时间 | 说明 |
|---------|---------|------|
| 工商信息 | 24小时 | 变更频率低 |
| 企业简介 | 7天 | 人工维护，更新少 |
| 风险扫描 | 4小时 | 需要相对实时 |
| 软件著作权 | 12小时 | 定期更新 |
| 对外投资 | 24小时 | 变更频率低 |

---

## 🐛 故障排查

### 常见问题

#### 1. 查询失败

**现象**: 返回 500 错误
**原因**: 企查查 Token 失效或积分不足
**解决**:
```bash
# 检查 Token
curl -X POST https://agent.qcc.com/mcp/company/stream \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# 检查积分余额
# 登录企查查官网查看
```

#### 2. 数据为空

**现象**: 某些维度返回空数据
**原因**: 企业可能无该类记录
**解决**: 正常情况，页面会显示"暂无记录"

#### 3. 跨域问题

**现象**: 前端请求失败
**原因**: 后端 CORS 配置
**解决**: 检查 `main.py` 中的 CORS 配置

---

## 📝 后续优化建议

### 功能增强

1. **缓存层**: 添加 Redis 缓存，减少重复查询
2. **数据对比**: 多次查询结果对比，发现变化
3. **风险预警**: 风险因子变化时自动提醒
4. **导出报告**: 一键导出供应商尽调报告
5. **历史记录**: 查询历史记录和积分消耗统计

### 代码优化

1. **错误处理**: 更精细的错误分类和处理
2. **重试机制**: 失败自动重试
3. **限流保护**: 防止积分过快消耗
4. **日志记录**: 完整的查询日志
5. **单元测试**: 添加测试用例

---

## 📚 相关文档

- [企查查 MCP 测试报告](./企查查MCP测试报告.md)
- [企查查 MCP 积分优化报告](./企查查MCP积分优化报告.md)
- [北京振华永创智能科技有限公司尽调报告](./北京振华永创智能科技有限公司尽职调查报告.md)
- [企查查 MCP 部署指南](./docs/企查查MCP部署指南.md)

---

## 🎯 总结

### 已完成

- ✅ 企查查 MCP 客户端（Python）
- ✅ 后端 API 接口（5个维度）
- ✅ 前端 API 接口
- ✅ 供应商详情页面（Vue3）
- ✅ 低积分优化策略（节省 72% 积分）
- ✅ 综合评级系统（5维度评分）

### 技术栈

- **后端**: FastAPI + httpx + SQLite
- **前端**: Vue3 + Ant Design Vue + TypeScript
- **数据源**: 企查查 MCP (SSE 协议)
- **优化**: 并发查询 + 积分优化

### 积分消耗

- **单次查询**: ~7 积分
- **500积分可用**: ~71 次查询
- **对比全量**: 节省 ~18 积分/次

---

**开发完成**: 2026-07-13
**开发者**: Claude Code
**版本**: v1.0
