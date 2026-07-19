# G005：真实角色任务驾驶舱验收（2026-07-19）

> 阶段：阶段 3 / G005
>
> 范围：正式驾驶舱的真实数据契约、五视角、动作下钻、浏览器验证。
>
> 结论：**通过 G005 完成门，进入 G006 全量 QA 与最终评审。**
>
> 安全说明：本记录只保存接口契约、命令和汇总数量，不记录业务行数据或任何登录信息。

## 1. 完成范围

正式路由 `/dashboard/overview/index` 现在仅承载真实经营驾驶舱，不再以 `review=phase3` 切换评审 Demo。评审资产仍保留在独立目录，未被删除或混入生产入口。

1. 单路由提供**综合、经营、项目、财务、数据核验**五个决策视角。
2. 综合首屏顺序固定为：任务/缺口、风险/到期、数据可信度、角色摘要、最近变化。
3. 接口动作包含对象、原因、期限、责任人、状态和可消费下钻 Query。
4. 指标返回口径、来源、覆盖范围、核验状态与数据截止时间。
5. 正式动作只进入真实详情路由；未使用占位 Toast、双跳或隐式写入。

## 2. 实现要点

### 2.1 后端数据契约

- `GET /api/dashboard/overview` 改用 `get_readonly_db()`；聚合 GET 不建表、不提交、不写库。
- 新增三类下钻队列：`task_actions`、`risk_actions`、`verification_actions`。
- 每条动作固定提供 `object_id`、`reason`、`due_date`、`owner`、`status`、`target.path` 与 `target.query`。
- 新增 `data_contract`，为关键指标和来源记录返回指标口径、来源字段/视图、覆盖范围、核验状态、数据截止时间。
- 新增 `recent_changes`，只使用系统中已存的合同/项目业务时间，不构造“实时动态”。

### 2.2 正式驾驶舱

- 正式页使用 Vben `Page` 与既有 `StateBlock`，继续使用 `requestClient`。
- “数据核验”是正式视角，不依赖评审 Demo。
- 经营、项目、财务视角的行动区均消费后端动作契约，并以真实详情页完成下钻。
- 视角切换使用 `window.history.replaceState` 更新当前 hash Query，不重新挂载页面或重复聚合请求。
- 共享浅色工作台 token 增补驾驶舱分区、焦点、响应式与 `prefers-reduced-motion` 样式。

## 3. 验证证据

| 验证维度 | 当前证据 |
|---|---|
| 后端契约与只读 | `python -m pytest -q backend/tests/test_dashboard.py`：**5 passed** |
| 前端接口与源码边界 | `pnpm exec vitest run --environment node apps/web-antd/src/api/__tests__/dashboard.test.ts apps/web-antd/src/views/dashboard/overview/__tests__/dashboard-g005-source.test.ts apps/web-antd/src/views/dashboard/overview/phase3-review/__tests__/review-data.test.ts`：**3 files / 8 tests passed** |
| 生产构建 | `pnpm exec vite build --mode production`：**通过**；既有动态导入与大分块警告列入 G006 性能治理 |
| 真实浏览器 | `python scripts/verify_g005_dashboard_browser.py`：**通过** |
| 浏览器稳定性 | 初次聚合单请求；四个切换视角不重复聚合；详情下钻携带 `id`；无 `pageerror`、`requestfailed`、业务 HTTP 4xx/5xx |
| 数据库零变更 | SHA-256：`45353085257E5EE93CBD98889911631B7A793D51474559C6DBCA5EB6859C7C64`（验证前后相同） |

浏览器结构化结果：`docs/audits/assets/stage3-g005-dashboard-browser.json`。

## 4. 业务边界确认

- 不声明实时性、健康度、同比、已连接外部系统或自动匹配完成。
- 关键镜像数据默认显示为“待核验”；空责任人和空期限不被伪造成已知值。
- 数据核验页把“没有已识别缺口”与“数据已完整核验”明确区分。
- 页面加载、视角切换和详情读取均未触发业务写请求。

## 5. G006 后续门禁

G005 已完成，但不替代 G006。后续仍需完成：

- 全量后端、Vitest、类型检查、Lint、生产构建基线。
- 四视口全链路、加载/空/错误/无权限/弱网/冲突/陈旧数据验证。
- axe、键盘焦点、触控尺寸、对比度与 reduced-motion 验收。
- 网络、写请求、数据库零变更与独立 reviewer 审核。