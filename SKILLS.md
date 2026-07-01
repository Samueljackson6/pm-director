# SKILLS.md - pm-director 技能配置

> 本 Agent 专属的技能索引
> 自动从 `agents-comm/shared/SKILLS_INDEX.json` 同步
> 最后更新：2026-04-14 21:36

---

## 📋 我的技能列表

## ⚠️ 强制触发规则

**以下场景必须使用对应技能：**

| 场景 | 必须使用 | 禁止使用 |
|------|---------|---------|
| 微信公众号文章 (mp.weixin.qq.com) | web-content-fetcher | web_fetch, browser |
| 用户纠正 | 记录到 .learnings/LEARNINGS.md | 忽略 |


### 核心技能

| 技能 | 触发条件 | 优先级 |
|------|---------|--------|
| portfolio-watcher | triggers: | 🟡 中 |
| ontology | Typed, entities, know | 🟡 中 |
| web-content-fetcher |  | 🔴 高 |
| aminer-academic-search | Triggers:, "查学者",, "学术数据", | 🟡 中 |
| find-skills | compliance,, For, 技能, | 🟡 中 |
| stock-analysis | triggered, alerts, Check | 🟡 中 |
| skill-creator-latest | also, existing, want | 🟡 中 |
| codex-sub-agents | gpt-5-codex., review,, fix | 🟡 中 |

### 可选技能

| 技能 | 触发条件 | 优先级 |
|------|---------|--------|
| workflow-automation |  | 🟡 中 |
| openclaw-backup-tool |  | 🟡 中 |
| claude-code |  | 🟡 中 |
| memory-manager |  | 🟡 中 |
| subagent-overseer |  | 🟡 中 |
| file-manager |  | 🟡 中 |
| subagent-architecture |  | 🟡 中 |
| multi-search-engine |  | 🟡 中 |
| office-document-specialist-suite |  | 🟡 中 |
| openai-whisper |  | 🟡 中 |
| self-improving-agent |  | 🟡 中 |
| aliyun-bailian-image |  | 🟡 中 |
| memory-setup |  | 🟡 中 |
| desktop-control |  | 🟡 中 |
| lidan-writing-framework |  | 🟡 中 |
| daily-report-pdf |  | 🟡 中 |
| crypto-market-data |  | 🟡 中 |
| news-aggregator-skill |  | 🟡 中 |
| baidu-hot-monitor |  | 🟡 中 |
| rss-reader-skill |  | 🟡 中 |
| instreet |  | 🟡 中 |
| agent-browser |  | 🟡 中 |
| quant-strategy |  | 🟡 中 |
| wechat-article-publisher |  | 🟡 中 |
| wechat-article-writer |  | 🟡 中 |
| subagent-context-compactor |  | 🟡 中 |
| a-stock-analysis-1-0-0 |  | 🟡 中 |
| tavily-search-pro |  | 🟡 中 |
| tushare-finance |  | 🟡 中 |
| pua-skill |  | 🟡 中 |
| rss-digest |  | 🟡 中 |
| self-improving-agent-cn |  | 🟡 中 |
| info-designer-infographic |  | 🟡 中 |
| stock-market-pro |  | 🟡 中 |
| frontend-design-3 |  | 🟡 中 |
| chart-image |  | 🟡 中 |
| mx-data |  | 🟡 中 |
| stock-monitor-skill |  | 🟡 中 |
| instreet-wisdom |  | 🟡 中 |
| ai-financial-report-cn |  | 🟡 中 |
| subagent-driven-development-3 |  | 🟡 中 |
| backtest-expert |  | 🟡 中 |
| mx-toolbox |  | 🟡 中 |
| skillhub-preference |  | 🟡 中 |
| technical-indicators |  | 🟡 中 |
| summarize |  | 🟡 中 |
| portfolio-tracker |  | 🟡 中 |
| humanizer |  | 🟡 中 |
| agent-wisdom |  | 🟡 中 |
| proactive-agent |  | 🟡 中 |
| session-auto-archive |  | 🟡 中 |
| skill-vetter |  | 🟡 中 |
| market-sentiment |  | 🟡 中 |
| tencent-docs |  | 🟡 中 |
| subagent-tracker |  | 🟡 中 |
| akshare-stock-1-0-1 |  | 🟡 中 |
| a-stock-kline-analyzer |  | 🟡 中 |

---

## ⚠️ 重要规则

### 微信公众号文章
**必须使用 `web-content-fetcher` skill**
- ✅ 正确：使用 web-content-fetcher skill
- ❌ 错误：web_fetch 或 browser

### 外部操作
- 运维操作 → 转发 oc-ops
- 外部消息 → 先确认再发

### 学习记录
用户纠正时 → 记录到 `.learnings/LEARNINGS.md`

---

## 📁 索引文件

- 完整索引: `agents-comm/shared/SKILLS_INDEX.json`
- 触发规则: `agents-comm/shared/SKILLS_TRIGGER_RULES.md`

---

*此文件自动同步，请勿手动修改*
