# REDESIGN 规划交接提示

```text
/make-plan 为 PM Director 阶段3制定一份可实施的重设计计划。必须先读取 DESIGN-IS-2026-07-15/00-scope.md、01-evidence.md、02-scorecard.md、03-verdict.md，以及 docs/深度需求分析与架构设计-v2.md、docs/合同识别规则库-科研与服务类项目专项.md、docs/数据补全-合同条款调研与规律总结-20260709.md、docs/合同详情页整体改造方案-20260711.md、docs/vben-framework-rules.md。计划必须：1）以合同原件和来源核验为当前主任务；2）分离客户应收链与供应商应付链；3）支持科研/服务/物资双轴分类、ZH02/SGSC/财务编号别名、阶段与付款多对多及质保金例外；4）在真实 Vben Page、VxeGrid、Form、Drawer、StateBlock、ECharts 和后端动态菜单中实现评审 Demo；5）默认浅色、减少大块暗色，科技感集中在证据链与关系可视化；6）为小程序/App 定义共享 API/状态与独立移动任务流；7）所有模拟、推断、待核验、来源批次和数据时点必须明确标识；8）先交付业务模型、信息架构、兼容矩阵和关键任务流，再编码 Demo；9）不修改生产数据，任何数据库清洗需单独业务授权；10）包含测试、回退、验收和文档归档步骤。
```
