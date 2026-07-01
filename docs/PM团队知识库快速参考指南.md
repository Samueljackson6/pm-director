# PM 团队知识库快速参考指南

> **最后更新**：2026-06-24
> **适用对象**：pm-director 及 PM 团队所有成员

---

## 🚀 启动时必做（3 步，< 5 秒）

```bash
# 1. 加载身份
read IDENTITY.md

# 2. 加载长期记忆
read MEMORY.md

# 3. 加载知识库索引 ⭐ 最重要
read knowledge-base/index.md
```

---

## 📂 知识库结构

```
knowledge-base/
├── index.md                    # 总索引（启动必读）
├── 方法论/                     # 项目管理方法论
│   ├── 合同识别规则库.md
│   └── 合同识别自动学习机制.md
└── （待扩展）

docs/                           # 工具文档
├── OCR识别架构方案-最终版.md
├── PP-StructureV3集成方案.md
├── 合同编号纠错方案-修正版.md
└── ...（15+ 文档）

/home/samuel/projects/          # 项目工作区
```

---

## 🔍 快速查找

### 按场景查找

| 场景 | 文档位置 |
|------|---------|
| 合同识别 | `knowledge-base/方法论/合同识别规则库.md` |
| OCR 工具 | `docs/OCR识别架构方案-最终版.md` |
| 飞书表格维护 | `docs/飞书表格增量维护铁律.md` |
| 周报生成 | `skills/weekly-report/SKILL.md` |

### 按关键词搜索

```bash
# 搜索 PM 团队知识库
./scripts/search-knowledge-v2.sh "关键词"

# 示例
./scripts/search-knowledge-v2.sh "合同识别"
```

---

## 📝 知识库使用规范

### ⚠️ 铁律（强制遵守）

```
❌ 禁止：不查询知识库直接执行任务
❌ 禁止：任务完成后不归档新知识
❌ 禁止：归档后不更新索引

✅ 强制：任务前必须查询知识库
✅ 强制：任务后必须归档新知识
✅ 强制：归档后必须更新索引
```

### 任务前（查询）

```bash
# 1. 查看索引
cat knowledge-base/index.md

# 2. 搜索关键词
./scripts/search-knowledge-v2.sh "关键词"

# 3. 读取文档
read knowledge-base/方法论/合同识别规则库.md
```

### 任务中（应用）

```
✅ 查询了知识库：合同识别规则库
✅ 应用了知识点：PP-StructureV3 识别流程
✅ 验证了效果：准确率 83.3%
```

### 任务后（归档）

```bash
# 1. 写入知识库
write knowledge-base/方法论/新方法论.md

# 2. 更新索引
# 在 knowledge-base/index.md 中添加：
# | [[方法论/新方法论]] | 描述 | 2026-06-24 | ⭐⭐⭐ |
```

---

## 🔄 维护任务

### 自动维护（已配置）

| 任务 | 频率 | 时间 |
|------|------|------|
| 短期记忆归档 | 每天 | 19:00 |
| 知识库维护 | 每周日 | 19:05 |

### 手动维护

```bash
# 知识库维护（去重、孤儿检测）
./scripts/maintain-knowledge.sh

# 短期记忆归档
./scripts/archive-daily-memory.sh

# 任务恢复检查
python3 scripts/task-recovery.py check
```

---

## 🛠️ 工具清单

| 工具 | 路径 | 用途 |
|------|------|------|
| 知识库搜索 | `scripts/search-knowledge-v2.sh` | 搜索知识库 |
| 知识库维护 | `scripts/maintain-knowledge.sh` | 定期维护 |
| 记忆归档 | `scripts/archive-daily-memory.sh` | 每日归档 |
| 任务恢复 | `scripts/task-recovery.py` | 中断恢复 |
| Cron 配置 | `scripts/setup-cron.sh` | 配置定时任务 |

---

## 📊 核心数据

- **知识库文件**：20+
- **方法论文件**：2
- **工具文档**：15+
- **技能数量**：2
- **脚本数量**：10+

---

## 🔗 相关资源

- **知识库索引**：`knowledge-base/index.md`
- **长期记忆**：`MEMORY.md`
- **工作规范**：`AGENTS.md`
- **团队设计**：`TEAM_DESIGN.md`
- **心跳机制**：`HEARTBEAT.md`

---

## 💡 常见问题

### Q1: 启动时应该先读哪个文件？

**A**: 按顺序读取：IDENTITY.md → MEMORY.md → knowledge-base/index.md

### Q2: 如何快速找到合同识别相关文档？

**A**: 
```bash
./scripts/search-knowledge-v2.sh "合同识别"
```

### Q3: 任务完成后需要做什么？

**A**: 
1. 归档新知识到 `knowledge-base/`
2. 更新 `knowledge-base/index.md`
3. 更新 `MEMORY.md`（如有必要）

### Q4: 如何查看维护报告？

**A**:
```bash
cat reports/knowledge-maintenance-$(date +%Y-%m-%d).md
```

### Q5: Gateway 重启后如何恢复任务？

**A**: 自动恢复。脚本会检测 `memory/.gateway-just-restarted` 标记。

---

## ⚡ 快速命令

```bash
# 搜索知识
./scripts/search-knowledge-v2.sh "关键词"

# 维护知识库
./scripts/maintain-knowledge.sh

# 归档记忆
./scripts/archive-daily-memory.sh

# 检查中断任务
python3 scripts/task-recovery.py check

# 查看知识库统计
cat knowledge-base/index.md | grep "总计"
```

---

*索引在手，知识不迷路。*
