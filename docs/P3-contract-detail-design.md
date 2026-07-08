# P3-1 合同详情页改版 — 架构设计

> 参考文档：`docs/合同管理模块设计方案-v3.0.md`、`docs/UI设计方案-合同管理系统.md`、`docs/vben-framework-rules.md`

---

## 1. 实现方案

### 1.1 后端

#### 端点扩展

**现有** `GET /api/contracts/detail?contract_id=xxx`

```json
{
  "code": 0,
  "data": {
    "contract": { /* 合同全部字段 */ },
    "stages": [ /* 阶段列表 */ ],
    "payments": [ /* 付款记录 */ ],
    "deliverables": [ /* 交付物 */ ]
  }
}
```

**扩展后** 增加字段：

```json
{
  "code": 0,
  "data": {
    "contract": { "...", "official_name", "sgsc_id", "estimated_amount" },
    "stages": [],
    "payments": [],
    "deliverables": [],
    "projects": [ /* 关联项目 */ ],
    "finance": {
      "contract_amount": 496.6,
      "invoiced_amount": 200.0,
      "received_amount": 150.0,
      "unreceived_amount": 50.0
    },
    "files": [ /* 合同文件 */ ]
  }
}
```

**新增** `POST /api/contracts/files/upload` — 上传合同文件

#### 数据库
- `projects` 表已存在
- `contract_project_link` 表已存在
- `contract_files` 表 — 需检查是否存在，如不存在则创建

### 1.2 前端

**重写** `views/contracts/detail.vue` 使用分栏布局：

```
左栏 60%                    右栏 40%
┌─────────────────────┬─────────────────────┐
│ 基本信息卡片          │ 财务汇总卡片          │
│ (合同编号/名称/金额)  │ (合同额/已开票/已回款) │
├─────────────────────┼─────────────────────┤
│ 关联项目列表          │ 合同文件列表          │
│ (项目名称/状态/负责人) │ (文件名称/上传时间)    │
├─────────────────────┴─────────────────────┤
│ 阶段甘特图 (ECharts 横向条形图)             │
├─────────────────────┬─────────────────────┤
│ 付款计划表            │ 交付物清单            │
└─────────────────────┴─────────────────────┘
```

---

## 2. 文件列表

### 后端（修改）
| 文件 | 动作 | 说明 |
|------|------|------|
| `backend/routers/contracts.py` | 修改 | 扩展 detail 端点，增加 projects/finance/files |
| `backend/routers/contracts.py` | 修改 | 新增 files upload/list 端点 |

### 前端（修改/新建）
| 文件 | 动作 | 说明 |
|------|------|------|
| `apps/web-antd/src/views/contracts/detail.vue` | **重写** | 完整重设计 |
| `apps/web-antd/src/api/contracts.ts` | 修改 | 增加文件上传 API |
| `apps/web-antd/src/views/contracts/components/` | **新建** | 子组件目录 |
| `.../stage-gantt.vue` | **新建** | ECharts 甘特图组件 |
| `.../finance-summary.vue` | **新建** | 财务汇总卡片 |
| `.../file-list.vue` | **新建** | 文件列表组件 |
| `.../project-list.vue` | **新建** | 关联项目列表 |

---

## 3. 任务列表（实现顺序）

| # | 任务 | 依赖 | 预估 |
|---|------|------|------|
| 1 | 后端：扩展 detail 端点（关联项目+财务汇总） | — | 30min |
| 2 | 后端：检查/创建 contract_files 表 + 上传/列表端点 | 1 | 30min |
| 3 | 前端：重写 detail.vue 布局 + 基础信息区 | — | 30min |
| 4 | 前端：关联项目列表组件 | 1,3 | 15min |
| 5 | 前端：财务汇总卡片组件 | 1,3 | 15min |
| 6 | 前端：阶段甘特图 ECharts 组件 | 3 | 30min |
| 7 | 前端：文件上传/预览组件 | 2,3 | 30min |
| 8 | QA：全量测试验证 | 1-7 | 30min |

---

## 4. 依赖包

当前项目已安装 ECharts（`@vben/plugins/echarts`），无需新增依赖。

---

## 5. 共享知识

- VxeTable 规则：`#/adapter/vxe-table` 导入，`:formatter` 代替 slot
- ECharts 规则：`EchartsUI` + `useEcharts` from `@vben/plugins/echarts`
- API 请求：`requestClient` from `#/api/request`，自动解包 data
- 路由控制：`backend/routers/auth.py` 的 menus，隐藏页面用 `visible: False`
- 后端数据库：`get_db()` from `backend.database`
