const routeMeta = {
  dashboard: ["驾驶舱"],
  contracts: ["合同履约", "合同台账"],
  "contract-detail": ["合同履约", "合同台账", "合同详情"],
  projects: ["合同履约", "项目执行"],
  "project-detail": ["合同履约", "项目执行", "项目详情"],
  receivables: ["客户应收", "应收台账"],
  suppliers: ["供应商履约", "供应商档案"],
  "supplier-detail": ["供应商履约", "供应商详情"],
};

const dashboardViews = {
  all: {
    label: "全局视图",
    subtitle: "聚焦现金、交付与风险，给出今天最值得处理的 3 件事。",
    kpis: [
      ["合同总额", "2,486.0 万元", "+12.6%", "较上季度", "file", "up"],
      ["执行中项目", "18", "+3", "本月新增", "project", "up"],
      ["应收余额", "326.8 万元", "18.4%", "占合同额", "wallet", "down"],
      ["高风险事项", "7", "-2", "较昨日", "alert", "up"],
    ],
  },
  management: {
    label: "经营视图",
    subtitle: "查看签约、收入与毛利变化，快速识别经营结构风险。",
    kpis: [
      ["本季签约", "680.0 万元", "+18.2%", "同比", "file", "up"],
      ["确认收入", "412.6 万元", "+9.4%", "同比", "project", "up"],
      ["综合毛利率", "32.8%", "+2.1pp", "较预算", "wallet", "up"],
      ["商机转化", "41.6%", "-1.2pp", "较上月", "alert", "down"],
    ],
  },
  projects: {
    label: "项目视图",
    subtitle: "沿项目里程碑观察交付节奏、负责人负荷与延期风险。",
    kpis: [
      ["按期项目", "14 / 18", "77.8%", "按期率", "project", "up"],
      ["本周里程碑", "9", "3", "今日需确认", "clock", "down"],
      ["待验收交付物", "12", "+4", "较上周", "file", "down"],
      ["平均进度", "68.4%", "+6.2pp", "较月初", "dashboard", "up"],
    ],
  },
  finance: {
    label: "财务视图",
    subtitle: "联动发票、回款和付款，先处理逾期与未匹配资金。",
    kpis: [
      ["已开票", "1,684.2 万元", "67.7%", "开票率", "file", "up"],
      ["累计回款", "1,357.4 万元", "80.6%", "回款率", "wallet", "up"],
      ["逾期应收", "86.5 万元", "+12.0", "较上月", "alert", "down"],
      ["待匹配回款", "6 笔", "待核验", "非金额 0", "link", "down"],
    ],
  },
};

const contracts = [
  { id: "HT-2026-018", name: "城市管廊智能监测平台", customer: "城建数字科技集团", amount: "386.0", project: "北区智慧隧道一期", status: "履约中", badge: "success", progress: "76%", next: "阶段三验收 · 07-22" },
  { id: "HT-2026-015", name: "变电站智能巡检系统", customer: "华东电网建设公司", amount: "248.6", project: "220kV 站点巡检升级", status: "待开票", badge: "warning", progress: "64%", next: "开票申请 · 今日" },
  { id: "HT-2026-011", name: "数据中心能效管控项目", customer: "云谷数据产业园", amount: "512.0", project: "二期能耗治理", status: "有风险", badge: "danger", progress: "48%", next: "交付物逾期 · 3 天" },
  { id: "HT-2026-006", name: "园区综合能源服务", customer: "临港产业发展集团", amount: "298.8", project: "综合能源托管", status: "履约中", badge: "success", progress: "82%", next: "月度结算 · 07-19" },
  { id: "HT-2025-052", name: "轨道交通设备运维平台", customer: "城市轨交运营公司", amount: "460.0", project: "设备运维平台升级", status: "待回款", badge: "warning", progress: "92%", next: "尾款到期 · 07-18" },
];

const projects = [
  { code: "XM-2026-042", name: "北区智慧隧道一期", contract: "HT-2026-018", owner: "陈启明", stage: "部署与联调", progress: 76, status: "按期", badge: "success", milestone: "阶段三验收 · 07-22" },
  { code: "XM-2026-037", name: "220kV 站点巡检升级", contract: "HT-2026-015", owner: "周嘉宁", stage: "现场实施", progress: 64, status: "需关注", badge: "warning", milestone: "第二批设备上线 · 07-20" },
  { code: "XM-2026-026", name: "二期能耗治理", contract: "HT-2026-011", owner: "杜文博", stage: "系统开发", progress: 48, status: "有风险", badge: "danger", milestone: "接口联调 · 已逾期 3 天" },
  { code: "XM-2026-019", name: "综合能源托管", contract: "HT-2026-006", owner: "梁思雨", stage: "运营服务", progress: 82, status: "按期", badge: "success", milestone: "月度报告 · 07-19" },
];

const suppliers = [
  { code: "GY-0098", name: "华云智联科技", category: "物联网设备", contracts: 4, invoice: "186.4", payment: "142.0", risk: "正常", badge: "success" },
  { code: "GY-0072", name: "星瀚系统集成", category: "系统集成", contracts: 3, invoice: "98.6", payment: "81.2", risk: "发票待核验", badge: "warning" },
  { code: "GY-0054", name: "中科传感技术", category: "传感器", contracts: 5, invoice: "264.0", payment: "220.0", risk: "正常", badge: "success" },
  { code: "GY-0031", name: "远桥工程服务", category: "施工服务", contracts: 2, invoice: "74.2", payment: "42.0", risk: "付款临期", badge: "danger" },
];

const appState = {
  route: "dashboard",
  params: {},
  review: "normal",
  contractSearch: "",
};

const main = document.querySelector("#main-content");
const breadcrumb = document.querySelector("#breadcrumb");
const reviewSelect = document.querySelector("#review-state");
const commandPanel = document.querySelector(".command-panel");
const globalSearch = document.querySelector("#global-search");

function svg(name) {
  return `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;
}

function parseHash() {
  const raw = location.hash.replace(/^#/, "") || "dashboard?view=all";
  const [route, query = ""] = raw.split("?");
  return { route: routeMeta[route] ? route : "dashboard", params: Object.fromEntries(new URLSearchParams(query)) };
}

function currentLocation() {
  return location.hash.replace(/^#/, "") || "dashboard?view=all";
}

function navigate(route, params = {}) {
  const next = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") next.set(key, String(value));
  });
  const query = next.toString();
  location.hash = `${route}${query ? `?${query}` : ""}`;
  closeMenu();
  closeCommand();
}

function navigateToDetail(route) {
  navigate(route, { from: currentLocation() });
}

function navigateBack(fallback) {
  const source = appState.params.from;
  if (source && !source.startsWith("http") && !source.startsWith("//")) {
    location.hash = source;
  } else {
    navigate(fallback);
  }
}

function pageHeading(eyebrow, title, description, actions = "") {
  return `<div class="page-heading"><div><div class="eyebrow">${eyebrow}</div><h1>${title}</h1><p>${description}</p></div><div class="heading-actions">${actions}</div></div>`;
}

function demoNotice(text) {
  return `<div class="demo-notice">${svg("link")}<span><strong>阶段3评审 Demo</strong> · ${text}，业务明细为脱敏模拟数据。</span><time>核验时间 2026-07-15 09:42</time></div>`;
}

function badge(text, tone = "neutral") {
  return `<span class="badge ${tone}">${text}</span>`;
}

function button(text, action, iconName = "arrow", kind = "") {
  return `<button class="button ${kind}" data-action="${action}">${svg(iconName)}<span>${text}</span></button>`;
}

function kpiCard(item, index) {
  const [label, value, trend, note, iconName, direction] = item;
  const path = index % 2 === 0 ? "M2 29 C18 24,22 8,39 15 S62 29,90 4" : "M2 23 C18 7,31 31,46 17 S69 5,90 11";
  const iconTone = ["", "cyan", "warning", "success"][index];
  return `<article class="kpi-card"><div class="kpi-top"><span class="kpi-label">${label}</span><span class="kpi-icon ${iconTone}">${svg(iconName)}</span></div><div class="kpi-value">${value}</div><div class="kpi-meta"><span class="trend-${direction === "up" ? "up" : "down"}">${trend}</span><span>${note}</span></div><svg class="sparkline" viewBox="0 0 92 34" aria-hidden="true"><path d="${path}" fill="none" stroke="var(--primary)" stroke-width="2"/><path d="M2 33 ${path.slice(1)} L90 34 L2 34Z" fill="var(--primary)" opacity=".06"/></svg></article>`;
}

function statePage() {
  const labels = routeMeta[appState.route];
  const title = labels[labels.length - 1];
  const states = {
    loading: ["refresh", `正在加载${title}`, "正在同步最新业务数据，请稍候。", "loading"],
    empty: ["file", `${title}暂无数据`, "当前筛选范围没有匹配记录，可清除筛选或返回驾驶舱。", "empty"],
    error: ["alert", `${title}加载失败`, "连接暂时不可用，已保留当前筛选条件。请重试。", "error"],
  };
  const [iconName, heading, copy, className] = states[appState.review];
  return `<section class="page">${pageHeading("REVIEW STATE", title, "使用评审状态切换器验证通用反馈与恢复动作。")}${demoNotice("当前展示通用页面状态")}
    <div class="state-block ${className}"><div class="state-content"><div class="state-visual">${svg(iconName)}</div><h2>${heading}</h2><p>${copy}</p>${appState.review === "loading" ? "" : `<button class="button primary" data-action="reset-review">${svg("refresh")}<span>${appState.review === "empty" ? "清除筛选" : "重新加载"}</span></button>`}</div></div></section>`;
}

function dashboardPage() {
  const view = dashboardViews[appState.params.view] ? appState.params.view : "all";
  const data = dashboardViews[view];
  const tabs = Object.entries(dashboardViews).map(([key, value]) => `<button class="${key === view ? "is-active" : ""}" data-view="${key}" data-testid="view-${key}">${value.label}</button>`).join("");
  return `<section class="page dashboard-page" data-testid="page-dashboard">
    ${pageHeading("OPERATING PULSE", "今日经营态势", data.subtitle, `${button("导出经营简报", "export", "download")} ${button("新建合同", "create", "plus", "primary")}`)}
    ${demoNotice("四个视图共用同一路由并通过 view 参数保持状态")}
    <div class="view-tabs" aria-label="驾驶舱视图">${tabs}</div>
    <div class="kpi-grid">${data.kpis.map(kpiCard).join("")}</div>
    <div class="dashboard-grid">
      <article class="panel">
        <div class="panel-head"><div class="panel-title"><h2>经营动能曲线</h2><p>签约与现金回收 · 单位 <code>万元</code></p></div><div class="panel-tools"><span class="live-dot"></span><span>实时口径</span></div></div>
        <div class="chart-wrap" role="img" aria-label="近六个月签约额总体上升，回款额在五月短暂回落后恢复">
          <svg viewBox="0 0 720 220" preserveAspectRatio="none"><defs><linearGradient id="areaA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--primary)" stop-opacity=".25"/><stop offset="1" stop-color="var(--primary)" stop-opacity="0"/></linearGradient></defs><path d="M0 178 C65 168,74 95,144 112 S226 146,288 92 S372 52,432 78 S524 116,576 56 S655 29,720 44 L720 220 L0 220Z" fill="url(#areaA)"/><path d="M0 178 C65 168,74 95,144 112 S226 146,288 92 S372 52,432 78 S524 116,576 56 S655 29,720 44" fill="none" stroke="var(--primary)" stroke-width="3" vector-effect="non-scaling-stroke"/><path d="M0 196 C64 178,83 142,144 154 S226 171,288 132 S372 96,432 116 S518 148,576 102 S662 66,720 80" fill="none" stroke="var(--cyan)" stroke-width="2" stroke-dasharray="5 4" vector-effect="non-scaling-stroke"/></svg>
          <div class="chart-axis"><span>2月</span><span>3月</span><span>4月</span><span>5月</span><span>6月</span><span>7月</span></div>
        </div>
        <div class="chart-legend"><span><i></i>签约额 2,486.0</span><span><i></i>回款额 1,357.4</span></div>
        <div class="lane-list"><div class="lane-row"><span>合同转项目</span><div class="progress-track"><i style="width:88%"></i></div><strong>88%</strong></div><div class="lane-row"><span>里程碑按期</span><div class="progress-track"><i style="width:77.8%"></i></div><strong>77.8%</strong></div><div class="lane-row"><span>现金回收</span><div class="progress-track warning"><i style="width:80.6%"></i></div><strong>80.6%</strong></div></div>
      </article>
      <article class="panel">
        <div class="panel-head"><div class="panel-title"><h2>今天先处理</h2><p>按资金与交付影响排序 · 3 项</p></div><span class="badge danger">7 项风险</span></div>
        <div class="action-list">
          <button class="action-item" data-route="receivables" data-tab="invoice" data-filter="overdue" data-testid="action-overdue"><span class="action-icon danger">${svg("alert")}</span><span class="action-copy"><strong>2 笔客户发票已逾期</strong><small>合计 86.5 万元 · 最长逾期 12 天</small></span>${svg("chevron")}</button>
          <button class="action-item" data-detail="contract" data-testid="action-deliverable"><span class="action-icon">${svg("clock")}</span><span class="action-copy"><strong>项目交付物逾期 3 天</strong><small>二期能耗治理 · 责任人杜文博</small></span>${svg("chevron")}</button>
          <button class="action-item" data-route="supplier-detail" data-tab="invoice"><span class="action-icon info">${svg("link")}</span><span class="action-copy"><strong>6 笔回款等待匹配</strong><small>状态为待核验，未被显示为金额 0</small></span>${svg("chevron")}</button>
        </div>
        <div class="panel-head" style="margin-top:20px"><div class="panel-title"><h2>履约健康分布</h2><p>覆盖 18 个执行中项目</p></div></div>
        <div class="lane-list"><div class="lane-row"><span>健康</span><div class="progress-track"><i style="width:66%"></i></div><strong>12</strong></div><div class="lane-row"><span>需关注</span><div class="progress-track warning"><i style="width:28%"></i></div><strong>5</strong></div><div class="lane-row"><span>高风险</span><div class="progress-track warning"><i style="width:8%"></i></div><strong>1</strong></div></div>
      </article>
    </div>
  </section>`;
}

function contractsPage() {
  const keyword = appState.params.q || appState.contractSearch;
  const filtered = keyword ? contracts.filter((item) => `${item.id}${item.name}${item.customer}${item.project}`.toLowerCase().includes(keyword.toLowerCase())) : contracts;
  const rows = filtered.map((item) => `<tr><td><button class="entity-link" data-detail="contract">${item.name}</button><span class="cell-sub">${item.id}</span></td><td>${item.customer}</td><td><button class="entity-link" data-detail="project">${item.project}</button></td><td class="amount">${item.amount} 万元</td><td>${badge(item.status, item.badge)}</td><td><div class="progress-track"><i style="width:${item.progress}"></i></div><span class="cell-sub">${item.progress}</span></td><td>${item.next}</td><td><button class="button small" data-detail="contract">查看详情 ${svg("arrow")}</button></td></tr>`).join("");
  return `<section class="page" data-testid="page-contracts">
    ${pageHeading("CONTRACT FULFILLMENT", "合同台账", "从合同出发，联动项目、交付、开票与回款；每一行都能进入可追溯的履约上下文。", `${button("导出台账", "export", "download")} ${button("新建合同", "create", "plus", "primary")}`)}
    ${demoNotice("筛选条件写入当前 URL，详情返回时保留筛选上下文")}
    <div class="filter-bar"><label class="field search">${svg("search")}<input id="contract-search" value="${keyword}" placeholder="搜索合同编号、名称或客户" /></label><label class="field">${svg("filter")}<select aria-label="履约状态"><option>全部状态</option><option>履约中</option><option>有风险</option><option>待回款</option></select></label><label class="field"><select aria-label="负责人"><option>全部负责人</option><option>陈启明</option><option>杜文博</option></select></label><button class="button small primary" data-action="apply-contract-filter">应用筛选</button><span class="filter-count">共 <strong>${filtered.length}</strong> 条</span></div>
    <div class="summary-grid"><div class="summary-card"><span>合同总额</span><strong>2,486.0</strong><small>单位：万元</small></div><div class="summary-card"><span>履约中</span><strong>18</strong><small>占全部合同 42%</small></div><div class="summary-card"><span>待开票</span><strong>326.8</strong><small>单位：万元</small></div><div class="summary-card"><span>风险合同</span><strong>3</strong><small>其中高风险 1 项</small></div></div>
    <div class="table-card"><div class="table-toolbar"><div><h2>当前合同</h2><p>默认按下一行动时间排序</p></div><span class="badge info">条件可清除</span></div><div class="table-wrap"><table class="data-table"><thead><tr><th>合同</th><th>客户</th><th>关联项目</th><th>合同金额</th><th>状态</th><th>履约进度</th><th>下一行动</th><th>操作</th></tr></thead><tbody>${rows || `<tr><td colspan="8"><div class="state-content"><h2>没有匹配合同</h2><p>请调整关键词或清除筛选。</p><button class="button small" data-action="clear-contract-filter">清除筛选</button></div></td></tr>`}</tbody></table></div><div class="table-pagination"><span>显示 1–${filtered.length} 条，共 ${filtered.length} 条</span><div class="pager"><button aria-label="第1页" class="is-active">1</button><button aria-label="第2页">2</button><button aria-label="第3页">3</button></div></div></div>
  </section>`;
}

function projectsPage() {
  const rows = projects.map((item) => `<tr><td><button class="entity-link" data-detail="project">${item.name}</button><span class="cell-sub">${item.code}</span></td><td><button class="entity-link" data-detail="contract">${item.contract}</button></td><td>${item.owner}</td><td>${item.stage}</td><td><div class="progress-track"><i style="width:${item.progress}%"></i></div><span class="cell-sub">${item.progress}%</span></td><td>${badge(item.status, item.badge)}</td><td>${item.milestone}</td><td><button class="button small" data-detail="project">进入项目 ${svg("arrow")}</button></td></tr>`).join("");
  return `<section class="page" data-testid="page-projects">${pageHeading("PROJECT EXECUTION", "项目执行", "把合同承诺转成可跟踪的里程碑、交付物与责任人行动。", `${button("导出进度", "export", "download")} ${button("新建项目", "create", "plus", "primary")}`)}${demoNotice("项目正式菜单是生产实现的 P0 路由改造项")}
    <div class="summary-grid"><div class="summary-card"><span>执行中项目</span><strong>18</strong><small>本月新增 3 项</small></div><div class="summary-card"><span>平均进度</span><strong>68.4%</strong><small>较月初 +6.2pp</small></div><div class="summary-card"><span>本周里程碑</span><strong>9</strong><small>今日需确认 3 项</small></div><div class="summary-card"><span>逾期交付物</span><strong>4</strong><small>涉及 2 个项目</small></div></div>
    <div class="table-card"><div class="table-toolbar"><div><h2>项目履约队列</h2><p>按风险等级与里程碑时间排序</p></div><span class="badge warning">2 项需关注</span></div><div class="table-wrap"><table class="data-table"><thead><tr><th>项目</th><th>合同</th><th>负责人</th><th>当前阶段</th><th>进度</th><th>健康状态</th><th>下一里程碑</th><th>操作</th></tr></thead><tbody>${rows}</tbody></table></div></div>
  </section>`;
}

function chainHtml(current = 4) {
  const steps = [
    ["合同签订", "2026-02-18"],
    ["项目立项", "2026-02-26"],
    ["方案确认", "2026-03-22"],
    ["部署联调", "进行中"],
    ["客户验收", "计划 07-22"],
    ["回款闭环", "计划 08-15"],
  ];
  return `<div class="fulfillment-chain" data-testid="fulfillment-chain"><div class="chain-line"></div>${steps.map(([name, date], index) => `<div class="chain-step ${index + 1 < current ? "done" : index + 1 === current ? "current" : ""}"><span class="chain-node">${index + 1 < current ? svg("check") : `<b>${index + 1}</b>`}</span><strong>${name}</strong><small>${date}</small></div>`).join("")}</div>`;
}

function contractDetailPage() {
  const tab = appState.params.tab || "overview";
  const tabs = [["overview", "总览"], ["stage", "阶段与交付"], ["finance", "发票与回款"], ["risk", "风险记录"]].map(([key, label]) => `<button class="${tab === key ? "is-active" : ""}" data-detail-tab="${key}">${label}</button>`).join("");
  const tabContent = {
    overview: `<div class="info-grid"><div class="info-item"><span>客户</span><strong>城建数字科技集团</strong></div><div class="info-item"><span>合同类型</span><strong>技术服务</strong></div><div class="info-item"><span>负责人</span><strong>陈启明</strong></div><div class="info-item"><span>签订日期</span><strong class="mono">2026-02-18</strong></div><div class="info-item"><span>合同金额</span><strong class="mono">386.0 万元</strong></div><div class="info-item"><span>当前状态</span><strong>履约中 · 部署联调</strong></div></div>`,
    stage: `<div class="project-stage-list"><div class="project-stage"><span class="stage-index">S01</span><div><strong>需求与方案确认</strong><small>需求清单、总体方案、实施计划</small></div><span>已完成</span></div><div class="project-stage"><span class="stage-index">S02</span><div><strong>设备进场与部署</strong><small>完成 24 / 28 个点位</small></div><span>86%</span></div><div class="project-stage"><span class="stage-index">S03</span><div><strong>系统联调与试运行</strong><small>预计 2026-07-22 验收</small></div><span>进行中</span></div></div>`,
    finance: `<div class="finance-bars"><div class="finance-row"><div class="metric-row"><span>开票进度</span><strong>260.0 / 386.0 万元</strong></div><div class="progress-track"><i style="width:67.4%"></i></div></div><div class="finance-row"><div class="metric-row"><span>回款进度</span><strong>208.0 / 386.0 万元</strong></div><div class="progress-track"><i style="width:53.9%"></i></div></div><div class="finance-row"><div class="metric-row"><span>预算执行</span><strong>172.4 / 238.0 万元</strong></div><div class="progress-track warning"><i style="width:72.4%"></i></div></div></div>`,
    risk: `<div class="risk-list"><div class="risk-item">${svg("alert")}<div><strong>2 个部署点位等待客户协调</strong><small>影响预计 2 天，责任人陈启明，计划 07-17 前解决。</small></div></div><div class="risk-item">${svg("clock")}<div><strong>第三阶段验收材料待补充</strong><small>缺少试运行报告签章版本，计划 07-19 前完成。</small></div></div></div>`,
  }[tab];
  return `<section class="page" data-testid="page-contract-detail"><div class="detail-hero"><div class="back-row"><button class="back-link" data-action="back" data-fallback="contracts" data-testid="back-button">${svg("back")}<span>返回合同台账</span></button>${badge("履约中", "success")}</div><div class="detail-title"><div><div class="eyebrow">HT-2026-018 · CONTRACT</div><h1>城市管廊智能监测平台</h1><p><span>客户：城建数字科技集团</span><span>负责人：陈启明</span><span>数据时点：<code>2026-07-15 09:42</code></span></p></div><div class="health-score"><div><strong>86</strong><small>履约健康度</small></div></div></div></div>
    <div class="detail-layout"><div class="detail-main"><article class="detail-card"><div class="panel-head"><div><h2>履约链</h2><p>唯一强视觉中心 · 从合同承诺追踪到现金闭环</p></div><span class="badge info">当前：部署联调</span></div>${chainHtml(4)}</article>
      <article class="detail-card"><div class="panel-head"><div><h2>合同上下文</h2><p>阶段、财务与风险保持在同一对象中</p></div></div><div class="detail-tabs">${tabs}</div>${tabContent}</article></div>
      <aside class="detail-aside"><article class="detail-card"><h2>资金进度</h2><p>统一使用万元口径</p><div class="finance-bars"><div class="finance-row"><div class="metric-row"><span>已开票</span><strong>67.4%</strong></div><div class="progress-track"><i style="width:67.4%"></i></div></div><div class="finance-row"><div class="metric-row"><span>已回款</span><strong>53.9%</strong></div><div class="progress-track"><i style="width:53.9%"></i></div></div></div></article>
      <article class="detail-card"><h2>关联对象</h2><p>在业务上下文中逐级进入和返回</p><div class="linked-list"><div class="linked-item"><div><strong>北区智慧隧道一期</strong><small>XM-2026-042 · 执行中</small></div><button class="button small" data-detail="project">进入项目</button></div><div class="linked-item"><div><strong>客户发票 3 笔</strong><small>已开票 260.0 万元</small></div><button class="button small" data-route="receivables">查看</button></div></div></article>
      <article class="detail-card"><h2>下一步行动</h2><div class="risk-list"><div class="risk-item">${svg("clock")}<div><strong>确认验收材料</strong><small>截止 07-19 · 责任人陈启明</small></div></div></div><button class="button primary" style="width:100%;margin-top:12px" data-action="mark-done">${svg("check")}标记已处理</button></article></aside></div>
  </section>`;
}

function projectDetailPage() {
  return `<section class="page" data-testid="page-project-detail"><div class="detail-hero"><div class="back-row"><button class="back-link" data-action="back" data-fallback="projects" data-testid="back-button">${svg("back")}<span>返回来源页面</span></button>${badge("按期", "success")}</div><div class="detail-title"><div><div class="eyebrow">XM-2026-042 · PROJECT</div><h1>北区智慧隧道一期</h1><p><span>合同：HT-2026-018</span><span>负责人：陈启明</span><span>计划完成：<code>2026-08-10</code></span></p></div><div class="health-score"><div><strong>92</strong><small>项目健康度</small></div></div></div></div>
    <div class="detail-layout"><div class="detail-main"><article class="detail-card"><div class="panel-head"><div><h2>项目推进轨道</h2><p>承接合同履约链，突出当前阶段与责任边界</p></div><span class="badge info">总体进度 76%</span></div>${chainHtml(4)}</article><article class="detail-card"><h2>阶段执行</h2><p>交付物和责任人在阶段内聚合</p><div class="project-stage-list"><div class="project-stage"><span class="stage-index">01</span><div><strong>需求调研与设计</strong><small>8 项交付物全部验收 · 梁思雨</small></div><span>100%</span></div><div class="project-stage"><span class="stage-index">02</span><div><strong>设备部署</strong><small>24 / 28 个点位完成 · 周嘉宁</small></div><span>86%</span></div><div class="project-stage"><span class="stage-index">03</span><div><strong>系统联调</strong><small>接口联调与现场试运行 · 陈启明</small></div><span>58%</span></div><div class="project-stage"><span class="stage-index">04</span><div><strong>验收移交</strong><small>计划 2026-07-22 启动</small></div><span>待开始</span></div></div></article></div>
    <aside class="detail-aside"><article class="detail-card"><h2>项目快照</h2><div class="info-grid" style="grid-template-columns:1fr"><div class="info-item"><span>总体进度</span><strong class="mono">76%</strong></div><div class="info-item"><span>已投入成本</span><strong class="mono">172.4 万元</strong></div><div class="info-item"><span>下一里程碑</span><strong>阶段三验收 · 07-22</strong></div></div></article><article class="detail-card"><h2>风险与阻塞</h2><div class="risk-list"><div class="risk-item">${svg("alert")}<div><strong>2 个点位待客户协调</strong><small>预计影响 2 天，当前未影响总工期。</small></div></div></div></article><article class="detail-card"><h2>关联合同</h2><div class="linked-list"><div class="linked-item"><div><strong>城市管廊智能监测平台</strong><small>HT-2026-018</small></div><button class="button small" data-detail="contract">查看合同</button></div></div></article></aside></div>
  </section>`;
}

function receivablesPage() {
  const tab = appState.params.tab || "invoice";
  const tabs = `<div class="segment-tabs" data-count="2"><button class="${tab === "invoice" ? "is-active" : ""}" data-receivable-tab="invoice">发票台账</button><button class="${tab === "payment" ? "is-active" : ""}" data-receivable-tab="payment">回款记录</button></div>`;
  const invoiceRows = `<tr><td><button class="entity-link">FP-2026-0712</button><span class="cell-sub">增值税专用发票</span></td><td>城市管廊智能监测平台</td><td>城建数字科技集团</td><td class="amount">126.0 万元</td><td>${badge("已回款", "success")}</td><td>2026-06-28</td><td>已匹配 100%</td></tr><tr><td><button class="entity-link">FP-2026-0695</button><span class="cell-sub">增值税专用发票</span></td><td>轨道交通设备运维平台</td><td>城市轨交运营公司</td><td class="amount">86.5 万元</td><td>${badge("已逾期 12 天", "danger")}</td><td>2026-07-03</td><td>待催收</td></tr><tr><td><button class="entity-link">FP-2026-0688</button><span class="cell-sub">增值税普通发票</span></td><td>变电站智能巡检系统</td><td>华东电网建设公司</td><td class="amount">74.6 万元</td><td>${badge("部分回款", "warning")}</td><td>2026-07-10</td><td>已匹配 46%</td></tr>`;
  const paymentRows = `<tr><td><button class="entity-link">HK-2026-0481</button><span class="cell-sub">银行转账</span></td><td>城建数字科技集团</td><td class="amount">126.0 万元</td><td>2026-07-08</td><td>${badge("已匹配", "success")}</td><td>FP-2026-0712</td><td>自动匹配</td></tr><tr><td><button class="entity-link">HK-2026-0476</button><span class="cell-sub">银行转账</span></td><td>华东电网建设公司</td><td class="amount">34.6 万元</td><td>2026-07-06</td><td>${badge("部分匹配", "warning")}</td><td>FP-2026-0688</td><td>人工复核</td></tr><tr><td><button class="entity-link">HK-2026-0469</button><span class="cell-sub">摘要信息不完整</span></td><td>待核验客户</td><td class="amount muted">待核验</td><td>2026-07-04</td><td>${badge("待匹配", "danger")}</td><td>—</td><td>需补充银行流水</td></tr>`;
  const headers = tab === "invoice" ? ["发票", "项目", "客户", "开票金额", "状态", "开票日期", "匹配情况"] : ["回款流水", "客户", "回款金额", "到账日期", "匹配状态", "关联发票", "处理方式"];
  return `<section class="page" data-testid="page-receivables">${pageHeading("CUSTOMER RECEIVABLES", "客户应收", "统一查看发票、回款与匹配状态；逾期和待核验数据优先进入行动队列。", `${button("导出应收", "export", "download")} ${button(tab === "invoice" ? "登记发票" : "登记回款", "create", "plus", "primary")}`)}${demoNotice("金额统一使用万元，待核验记录不显示为 0")}
    <div style="margin-bottom:14px">${tabs}</div><div class="summary-grid"><div class="summary-card"><span>应收余额</span><strong>326.8</strong><small>单位：万元</small></div><div class="summary-card"><span>逾期应收</span><strong>86.5</strong><small>最长逾期 12 天</small></div><div class="summary-card"><span>本月回款</span><strong>218.6</strong><small>较上月 +11.2%</small></div><div class="summary-card"><span>待匹配</span><strong>6 笔</strong><small>其中 2 笔待核验金额</small></div></div>
    <div class="table-card"><div class="table-toolbar"><div><h2>${tab === "invoice" ? "客户发票" : "回款流水"}</h2><p>${appState.params.filter === "overdue" ? "已应用筛选：逾期记录" : "默认按资金风险排序"}</p></div>${appState.params.filter ? `<button class="button small" data-action="clear-receivable-filter">清除筛选</button>` : badge("口径：万元", "info")}</div><div class="table-wrap"><table class="data-table"><thead><tr>${headers.map((item) => `<th>${item}</th>`).join("")}</tr></thead><tbody>${tab === "invoice" ? invoiceRows : paymentRows}</tbody></table></div></div>
  </section>`;
}

function suppliersPage() {
  const rows = suppliers.map((item) => `<tr><td><button class="entity-link" data-detail="supplier">${item.name}</button><span class="cell-sub">${item.code}</span></td><td>${item.category}</td><td>${item.contracts} 份</td><td class="amount">${item.invoice} 万元</td><td class="amount">${item.payment} 万元</td><td>${badge(item.risk, item.badge)}</td><td><button class="button small" data-detail="supplier">履约详情 ${svg("arrow")}</button></td></tr>`).join("");
  return `<section class="page" data-testid="page-suppliers">${pageHeading("SUPPLIER FULFILLMENT", "供应商档案", "把供应商主体、合同、入站发票与付款放进同一个履约上下文。", `${button("导出档案", "export", "download")} ${button("新建供应商", "create", "plus", "primary")}`)}${demoNotice("生产实现前需修复供应商详情自重定向和付款接口地址")}
    <div class="summary-grid"><div class="summary-card"><span>合作供应商</span><strong>42</strong><small>本月新增 2 家</small></div><div class="summary-card"><span>有效采购合同</span><strong>68</strong><small>执行中 31 份</small></div><div class="summary-card"><span>本月入站发票</span><strong>284.6</strong><small>单位：万元</small></div><div class="summary-card"><span>待付款</span><strong>112.0</strong><small>7 日内到期 3 笔</small></div></div>
    <div class="table-card"><div class="table-toolbar"><div><h2>供应商履约队列</h2><p>按付款临期与资料核验状态排序</p></div><span class="badge warning">2 项需关注</span></div><div class="table-wrap"><table class="data-table"><thead><tr><th>供应商</th><th>分类</th><th>合同</th><th>入站发票</th><th>已付款</th><th>风险状态</th><th>操作</th></tr></thead><tbody>${rows}</tbody></table></div></div>
  </section>`;
}

function supplierDetailPage() {
  const tab = appState.params.tab || "overview";
  const tabs = [["overview", "履约总览"], ["invoice", "供应商发票"], ["payment", "付款记录"]].map(([key, label]) => `<button class="${tab === key ? "is-active" : ""}" data-supplier-tab="${key}">${label}</button>`).join("");
  const content = {
    overview: `<div class="info-grid"><div class="info-item"><span>统一社会信用代码</span><strong class="mono">91***********82X</strong></div><div class="info-item"><span>供应商分类</span><strong>物联网设备</strong></div><div class="info-item"><span>合作状态</span><strong>正常合作</strong></div><div class="info-item"><span>当前合同</span><strong>4 份</strong></div><div class="info-item"><span>合同总额</span><strong class="mono">268.0 万元</strong></div><div class="info-item"><span>企查查信息</span><strong>2026-07-14 已核验</strong></div></div>`,
    invoice: `<div class="record-list"><div class="record-item"><div class="record-top"><strong>INV-GY-2026-071 · 传感终端第二批</strong>${badge("已核验", "success")}</div><small>86.4 万元 · 2026-07-08 · 关联合同 CG-2026-026</small></div><div class="record-item"><div class="record-top"><strong>INV-GY-2026-064 · 网关与配件</strong>${badge("待核验", "warning")}</div><small>42.0 万元 · 2026-07-02 · 税额信息待复核</small></div></div>`,
    payment: `<div class="record-list"><div class="record-item"><div class="record-top"><strong>FK-2026-0382 · 第二阶段设备款</strong>${badge("已支付", "success")}</div><small>78.0 万元 · 2026-07-09 · 银行转账</small></div><div class="record-item"><div class="record-top"><strong>FK-2026-0401 · 第三阶段预付款</strong>${badge("待审批", "warning")}</div><small>32.0 万元 · 计划 2026-07-18 · 责任人周嘉宁</small></div></div>`,
  }[tab];
  return `<section class="page" data-testid="page-supplier-detail"><div class="detail-hero"><div class="back-row"><button class="back-link" data-action="back" data-fallback="suppliers" data-testid="back-button">${svg("back")}<span>返回供应商档案</span></button>${badge("正常合作", "success")}</div><div class="detail-title"><div><div class="eyebrow">GY-0098 · SUPPLIER</div><h1>华云智联科技</h1><p><span>分类：物联网设备</span><span>合作合同：4 份</span><span>数据时点：<code>2026-07-15 09:42</code></span></p></div><div class="health-score"><div><strong>90</strong><small>履约健康度</small></div></div></div></div>
    <div class="detail-layout"><div class="detail-main"><article class="detail-card"><div class="panel-head"><div><h2>供应商履约链</h2><p>采购合同、到货、发票与付款连续可追踪</p></div><span class="badge info">当前：付款审批</span></div>${chainHtml(5)}</article><article class="detail-card"><div class="detail-tabs">${tabs}</div>${content}</article></div>
    <aside class="detail-aside"><article class="detail-card"><h2>往来摘要</h2><div class="finance-bars"><div class="finance-row"><div class="metric-row"><span>已收票</span><strong>186.4 万元</strong></div><div class="progress-track"><i style="width:69.6%"></i></div></div><div class="finance-row"><div class="metric-row"><span>已付款</span><strong>142.0 万元</strong></div><div class="progress-track"><i style="width:53%"></i></div></div></div></article><article class="detail-card"><h2>下一步行动</h2><div class="risk-list"><div class="risk-item">${svg("clock")}<div><strong>确认第三阶段付款申请</strong><small>计划 07-18 · 金额 32.0 万元</small></div></div></div><button class="button primary" style="width:100%;margin-top:12px" data-action="mark-done">${svg("check")}标记已处理</button></article></aside></div>
  </section>`;
}

const renderers = {
  dashboard: dashboardPage,
  contracts: contractsPage,
  "contract-detail": contractDetailPage,
  projects: projectsPage,
  "project-detail": projectDetailPage,
  receivables: receivablesPage,
  suppliers: suppliersPage,
  "supplier-detail": supplierDetailPage,
};

function updateNavigation() {
  document.querySelectorAll(".nav-item, .nav-child").forEach((item) => item.classList.remove("is-active"));
  const selectors = {
    dashboard: '[data-route="dashboard"]',
    contracts: '[data-route="contracts"]',
    "contract-detail": '[data-route="contracts"]',
    projects: '[data-route="projects"]',
    "project-detail": '[data-route="projects"]',
    receivables: '[data-route="receivables"]',
    suppliers: '[data-route="suppliers"]',
    "supplier-detail": '[data-route="suppliers"]',
  };
  document.querySelector(selectors[appState.route])?.classList.add("is-active");
  breadcrumb.innerHTML = routeMeta[appState.route].map((item, index, list) => index === list.length - 1 ? `<strong>${item}</strong>` : `<span>${item}</span>${svg("chevron")}`).join("");
}

function render() {
  const parsed = parseHash();
  appState.route = parsed.route;
  appState.params = parsed.params;
  updateNavigation();
  main.innerHTML = appState.review === "normal" ? renderers[appState.route]() : statePage();
  main.scrollTop = 0;
  document.title = `${routeMeta[appState.route].at(-1)} · PM Director 阶段3 Demo`;
}

function showToast(message) {
  const region = document.querySelector(".toast-region");
  const item = document.createElement("div");
  item.className = "toast";
  item.innerHTML = `${svg("check")}<span>${message}</span>`;
  region.append(item);
  window.setTimeout(() => item.remove(), 2600);
}

function openCommand() {
  commandPanel.hidden = false;
  window.setTimeout(() => globalSearch.focus(), 0);
}

function closeCommand() {
  commandPanel.hidden = true;
  globalSearch.value = "";
}

function openMenu() {
  document.body.classList.add("menu-open");
  document.querySelector(".sidebar-close")?.focus();
}

function closeMenu() {
  const wasOpen = document.body.classList.contains("menu-open");
  document.body.classList.remove("menu-open");
  if (wasOpen) document.querySelector(".mobile-menu")?.focus();
}

document.addEventListener("click", (event) => {
  const target = event.target.closest("button, [data-action]");
  if (!target) return;

  if (target.dataset.route) {
    const params = {};
    if (target.dataset.tab) params.tab = target.dataset.tab;
    if (target.dataset.filter) params.filter = target.dataset.filter;
    navigate(target.dataset.route, params);
    return;
  }

  if (target.dataset.detail) {
    const routes = { contract: "contract-detail", project: "project-detail", supplier: "supplier-detail" };
    navigateToDetail(routes[target.dataset.detail]);
    return;
  }

  if (target.dataset.view) {
    navigate("dashboard", { view: target.dataset.view });
    return;
  }

  if (target.dataset.detailTab) {
    navigate("contract-detail", { ...appState.params, tab: target.dataset.detailTab });
    return;
  }

  if (target.dataset.receivableTab) {
    navigate("receivables", { tab: target.dataset.receivableTab });
    return;
  }

  if (target.dataset.supplierTab) {
    navigate("supplier-detail", { ...appState.params, tab: target.dataset.supplierTab });
    return;
  }

  const action = target.dataset.action;
  if (action === "toggle-group") {
    const group = target.closest(".nav-group");
    group.classList.toggle("is-open");
    target.setAttribute("aria-expanded", String(group.classList.contains("is-open")));
  } else if (action === "open-menu") {
    openMenu();
  } else if (action === "close-menu") {
    closeMenu();
  } else if (action === "focus-search") {
    openCommand();
  } else if (action === "toggle-theme") {
    const isDark = document.documentElement.dataset.theme === "dark";
    document.documentElement.dataset.theme = isDark ? "light" : "dark";
    document.querySelector(".theme-icon use").setAttribute("href", isDark ? "#i-moon" : "#i-sun");
    showToast(`已切换为<strong>${isDark ? "浅色" : "深色"}主题</strong>`);
  } else if (action === "back") {
    navigateBack(target.dataset.fallback || "dashboard");
  } else if (action === "export") {
    showToast("已生成<strong>评审版导出任务</strong>，Demo 不会下载真实业务数据");
  } else if (action === "create") {
    showToast("已打开<strong>新建流程占位</strong>，生产实现将复用 Vben 表单规范");
  } else if (action === "mark-done") {
    showToast("行动项已标记为<strong>模拟完成</strong>");
  } else if (action === "show-notice") {
    showToast("当前有<strong>7 项风险提醒</strong>，可从驾驶舱处理");
  } else if (action === "reset-review") {
    appState.review = "normal";
    reviewSelect.value = "normal";
    render();
  } else if (action === "apply-contract-filter") {
    const value = document.querySelector("#contract-search")?.value.trim() || "";
    appState.contractSearch = value;
    navigate("contracts", value ? { q: value, page: 1, sort: "next_action" } : {});
  } else if (action === "clear-contract-filter") {
    appState.contractSearch = "";
    navigate("contracts");
  } else if (action === "clear-receivable-filter") {
    navigate("receivables", { tab: appState.params.tab || "invoice" });
  }
});

reviewSelect.addEventListener("change", () => {
  appState.review = reviewSelect.value;
  render();
});

document.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    openCommand();
  }
  if (event.key === "Escape") {
    closeCommand();
    closeMenu();
  }
});

commandPanel.addEventListener("click", (event) => {
  if (event.target === commandPanel) closeCommand();
});

window.addEventListener("hashchange", render);

if (!location.hash) {
  navigate("dashboard", { view: "all" });
} else {
  render();
}
