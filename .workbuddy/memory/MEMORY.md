# PM-Director 项目记忆

## 数据治理 (2026-07-12)
- **全量清洗报告**: `docs/data-cleanup-report-2026-07-12.md`
- **42合同全部通过审计**, 阶段从1开始编号(合同签订之日=阶段1起始日)
- **科研类**: 阶段名="研究阶段5.1"~"5.N", remarks(主要内容)与 acceptance_criteria(考核目标)严格分离
- **技术服务类**: service_content 只含1.2节, 1.3→service_method, 2.1→location, 2.2→period, 2.3→schedule(新), 2.4→quality(新)
- **付款-阶段关联**: 33条付款已重建阶段引用("乙方完成研究阶段5.1~5.2约定内容...")
- **OCR清洗函数**: clean_ocr_text / split_remarks_and_khmb / is_ocr_garbage 可在其他项目复用
- **build:antd 命令**: `pnpm run build:antd` (包名=@vben/web-antd, 非 web-antd)

## 甘特图组件 (stage-gantt.vue)
- **渲染方案**: 使用 ECharts `type: 'custom'` + `renderItem`，核心是 `api.coord` 调用
- **关键修复**: `api.coord([timeValue, yValue])` 的 yValue 必须传**类别标签字符串**（如 `'研究阶段5.1'`）而非数字索引（`0`），否则某些 ECharts 版本无法正确渲染
- **bandHeight 计算**: 通过 `api.coord([time, currentLabel])` 和 `api.coord([time, nextLabel])` 的 y 坐标差手动计算
- **降级策略**: ECharts 异常→纯 HTML 清单模式

## 合同列表 (index.vue)
- 使用 Vben VxeTable + `proxyConfig.ajax.query` 分页查询
- `current_finance_view` 通过 contract_id 关联，SGSC 合同需经 `contract_id_mapping` 转 ZH ID

## 合同详情 (detail.vue)
- 后端 API 通过 `contract_id_mapping` 将 SGSC ID 映射到 ZH canonical ID 再查关联表
- 条款默认折叠 (`:default-active-key="[]"`)
- 服务内容>150字可展开/收起

## 后端数据库规则
- **path**: `/app/database/project_management.db`
- **新增列**: contracts.service_schedule, contracts.service_quality
- **personnel**: 34人（从contacts去重）
- **project_personnel**: 101行
- **suppliers**: 55个（从contracts甲乙方去重）
