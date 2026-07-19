# 阶段 3 G006：业务范围无障碍与最终 QA 经验

> 日期：2026-07-19
>
> 适用范围：Vben + Ant Design Vue + VxeTable 业务纵向切片的最终验收。

## 可复用结论

1. **axe 范围必须有业务边界且可验证。** 对业务页面使用唯一 `.pm-workbench-page` 根节点运行 WCAG 2 A/AA；脚本先断言该根节点唯一，不能用全局规则静默忽略框架问题。
2. **第三方 ARIA 问题应做最小适配。** Ant Design Vue 4.2.x 关闭下拉时可能保留悬空的组合框引用；适配层应补齐可访问名称和 `aria-expanded`，并在列表未挂载时清理悬空引用。
3. **宽表滚动区要能被键盘进入。** 对 VxeTable 的表头、表体可滚动内层增加 `role="region"`、可读标签和 `tabindex="0"`，并通过 DOM 更新观察器应对异步渲染。
4. **最终 QA 同时验证读写边界。** 浏览器脚本要记录 `pageerror`、失败请求、业务 HTTP 失败和 API 写请求，并将数据库 SHA-256 前后比较作为零变更证据。
5. **存量债务须与本次回归分开报告。** 全仓 TypeScript、全仓 Lint、构建警告和框架壳层问题不能因业务切片通过而被表述为全绿。
6. **按钮文本的视觉字间距不能当作稳定的可访问名称。** Ant Design Vue 按钮可能向自动化可访问树暴露“查 询”而不是“查询”；当页面的业务语义稳定时，应显式提供 `aria-label`，同时提升读屏和 Playwright 选择器的稳定性。
7. **TypeScript 收口应按改造域和全仓两层报告。** 最新 `vue-tsc` 可证明阶段 3 路径为 0 项错误，但全仓仍有 354 项跨模块债务；两者不可互相替代。
8. **缓存忽略只应覆盖缓存。** 将 `.turbo` 加入 Prettier 忽略规则可消除缓存目录噪声，但不能据此忽略 `src` 或掩盖业务文件的格式/排序问题。

## 本次证据

- 后端：39 passed。
- Vitest：60 files / 379 tests passed。
- 浏览器：17 条任务、32 条四视口、6 条驾驶舱、6 条状态检查通过；5 个业务页 axe 无 Critical / Serious；数据库前后一致。
- 静态复验：阶段 3 改造域 TypeScript 0 项；全仓 TypeScript 354 项存量错误；受影响业务文件 ESLint 1360 errors / 7 warnings，未宣称 Lint 通过。
- 审计报告：`docs/audits/stage3-g006-final-qa-20260719.md`。
