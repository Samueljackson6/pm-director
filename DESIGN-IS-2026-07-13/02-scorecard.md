# Dieter Rams 十原则评分

1. Good design is innovative — Score: 1/3  
   Evidence: 当前主要是常见后台卡片、表格、Tab 和侧栏组合，见 `01-evidence.md#十原则对应事实`。  
   Justification: 它模仿成熟后台模式并有少量业务化组合，但没有形成明显改善同类流程的新模式。

2. Good design makes a product useful — Score: 0/3  
   Evidence: 供应商主入口 404，项目和旧发票只能绕过菜单直达，见 `01-evidence.md#结构证据`。  
   Justification: 按最差代表实例评分，至少一个核心业务任务在审计页面上不能直接完成。

3. Good design is aesthetic — Score: 1/3  
   Evidence: 31 种引用色、最低对比度约 2.17:1、新旧页面和多层导航并存，见 `01-evidence.md#视觉证据`。  
   Justification: 基础栅格仍可辨认，但已出现一个以上刺眼违例和多处系统不一致，不能评为 2。

4. Good design makes a product understandable — Score: 0/3  
   Evidence: 同一业务有新旧路径，返回进入无菜单页面，供应商返回 404，见 `01-evidence.md#文案与诚实性证据`。  
   Justification: 用户无法仅凭界面判断当前页面来源和返回目标，核心导航功能需要外部解释。

5. Good design is unobtrusive — Score: 1/3  
   Evidence: 顶部菜单、侧栏、页面 Tab 与密集卡片同时出现，见 `01-evidence.md#结构证据`。  
   Justification: 内容仍是主体，但重复导航和装饰性卡片持续与内容竞争注意力。

6. Good design is honest — Score: 1/3  
   Evidence: 单位、风险、评级、导出和返回标签存在多处行为不一致，见 `01-evidence.md#文案与诚实性证据`。  
   Justification: 没有暗黑模式，但远超过两个夸大或标签行为错配，只能评为 1。

7. Good design is long-lasting — Score: 1/3  
   Evidence: Emoji、渐变、过多圆角 KPI 卡片和通用后台模板并存，见 `01-evidence.md#十原则对应事实`。  
   Justification: 存在两到三个明显的阶段性视觉标记，整体会快速显得过时。

8. Good design is thorough down to the last detail — Score: 2/3  
   Evidence: 六类状态均存在，但键盘语义、对比度、无效按钮和供应商错误处理粗糙，见 `01-evidence.md#视觉证据`、`#可访问性证据`。  
   Justification: 状态覆盖较完整，因此高于 1；但至少一类状态和多个细节仍粗糙，不能评为 3。

9. Good design is environmentally friendly — Score: 0/3  
   Evidence: 初始 JS 约 4.07MB、87 个请求、一次 TTI 超过 60 秒，见 `01-evidence.md#性能与摩擦证据`。  
   Justification: 按明确锚点，初始 JS 超过 2MB 即为 0。

10. Good design is as little design as possible — Score: 0/3  
    Evidence: 三层导航、旧新路由、旧新页面和重复交互同时存在，见 `01-evidence.md#结构证据`。  
    Justification: 页面和系统被重复 affordance 主导，删除其中多项不会破坏任务，反而会提升清晰度。

## 总分

**7/30**

评分规则：按最差代表实例评分；不取平均；不加权；不因已有代码量而提高分数。
