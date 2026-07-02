# OCR识别架构方案（最终版）

> **确定时间**：2026-06-24 12:48  
> **核心原则**：主力使用PaddleOCR+PP-StructureV3，百度OCR仅作备选

---

> **⚠️ 2026-07-02 重要更新**：
> 当前合同数据**不再依赖 PDF OCR 识别**。所有 35 个合同已通过**人工手动 OCR** 转换为 .docx 文件，
> 存放于 236 服务器 `/home/samuel/OCdoc/已ocr合同`。PDF 扫描件仅作为原始合同存档和审计对照使用。
>
> 本文档保留作技术参考，OCR 工具（PP-StructureV3）在以下场景保留启用：
> - 新增合同尚未手动 OCR 时
> - 需要交叉验证人工提取的数据时
>
> **详见**：`docs/合同识别数据源说明-20260702.md`

## 一、架构原则

### 1.1 主力方案

**✅ PaddleOCR + PP-StructureV3（主力，优先使用）**

| 优势 | 说明 |
|------|------|
| ✅ **本地部署** | 数据安全，不上传云端 |
| ✅ **完全免费** | 无限制，无额度限制 |
| ✅ **准确率高** | 综合准确率83.3%（vs 百度OCR 61.1%） |
| ✅ **甲乙方识别优秀** | 识别率100%（vs 百度OCR 33.3%） |
| ✅ **表格识别专业** | 支持跨行跨列，自动检测 |

**使用场景**：
- ✅ **日常所有合同识别**
- ✅ **批量处理**
- ✅ **敏感数据处理**
- ✅ **复杂表格识别**

---

### 1.2 备选方案

**⚠️ 百度OCR（备选，非必要不使用）**

| 优势 | 说明 |
|------|------|
| ✅ 云端服务 | 无需本地部署 |
| ✅ 识别速度快 | API调用即时返回 |
| ⚠️ 有限免费额度 | 有使用限制 |
| ⚠️ 数据上传云端 | 数据安全风险 |

**使用场景**：
- ⚠️ **仅当本地PaddleOCR出现问题时**
- ⚠️ **紧急情况下的临时方案**
- ⚠️ **非敏感数据的快速识别**

---

## 二、智能路由策略

### 2.1 优先级路由

```python
def choose_ocr_engine(contract_type, sensitivity, local_available=True):
    """
    选择OCR引擎
    
    优先级：
    1. PaddleOCR + PP-StructureV3（主力）
    2. 百度OCR（备选）
    """
    
    # 优先使用本地PaddleOCR
    if local_available:
        return {
            "engine": "PaddleOCR + PP-StructureV3",
            "reason": "主力方案，准确率高，免费无限制"
        }
    
    # 本地不可用时，使用百度OCR（备选）
    return {
        "engine": "百度OCR",
        "reason": "备选方案，仅当本地不可用时使用",
        "warning": "注意：有额度限制，数据上传云端"
    }
```

---

### 2.2 场景路由表

| 场景 | 优先方案 | 备选方案 | 触发条件 |
|------|---------|---------|---------|
| **日常合同识别** | PaddleOCR + PP-StructureV3 | 百度OCR | 本地不可用 |
| **批量处理** | PaddleOCR + PP-StructureV3 | - | 强制使用本地 |
| **敏感数据** | PaddleOCR + PP-StructureV3 | - | 强制使用本地 |
| **复杂表格** | PaddleOCR + PP-StructureV3 | - | 强制使用本地 |
| **紧急识别** | PaddleOCR + PP-StructureV3 | 百度OCR | 本地失败 |
| **测试验证** | 百度OCR | - | 仅用于对比测试 |

---

## 三、使用规范

### 3.1 默认使用PaddleOCR

**所有合同识别任务默认使用PaddleOCR + PP-StructureV3**

```python
# 默认流程
def recognize_contract(pdf_path):
    # 1. 优先使用PaddleOCR + PP-StructureV3
    result = paddleocr_recognize(pdf_path)
    
    # 2. 检查识别质量
    if result['quality'] >= 0.8:  # 置信度阈值
        return result
    
    # 3. 质量不达标，记录日志
    log_warning(f"PaddleOCR识别质量低: {result['quality']}")
    
    # 4. 返回结果（仍使用PaddleOCR，但标记质量）
    result['quality_warning'] = True
    return result
```

---

### 3.2 使用百度OCR的条件

**严格限制使用百度OCR，仅以下情况可用：**

| 条件 | 说明 | 示例 |
|------|------|------|
| ✅ **本地PaddleOCR服务不可用** | 服务崩溃、模型损坏 | "PaddleOCR服务异常" |
| ✅ **紧急情况** | 用户明确要求快速识别 | "现在就要结果" |
| ✅ **对比测试** | 用于验证PaddleOCR效果 | "对比百度OCR和PaddleOCR" |
| ❌ **日常使用** | 禁止 | - |
| ❌ **批量处理** | 禁止 | - |
| ❌ **敏感数据** | 禁止 | - |

---

### 3.3 使用百度OCR的审批流程

```python
def use_baidu_ocr(reason, user_approved=False):
    """
    使用百度OCR需要审批
    
    Args:
        reason: 使用原因
        user_approved: 用户是否批准
    """
    
    # 检查原因
    valid_reasons = [
        "PaddleOCR服务不可用",
        "紧急识别需求",
        "对比测试验证"
    ]
    
    if reason not in valid_reasons:
        raise Exception(f"无效原因: {reason}，百度OCR仅用于备选")
    
    # 检查用户批准
    if not user_approved:
        raise Exception("使用百度OCR需要用户明确批准")
    
    # 记录使用日志
    log_info(f"使用百度OCR，原因: {reason}")
    
    # 执行百度OCR识别
    return baidu_ocr_recognize()
```

---

## 四、数据统计

### 4.1 综合验证结果（基于3份合同）

| 指标 | PaddleOCR + PP-StructureV3 | 百度OCR |
|------|---------------------------|---------|
| **综合准确率** | **83.3%** | 61.1% |
| **甲乙方识别** | **100%** | 33.3% |
| **合同名称识别** | 100% | 100% |
| **签订日期识别** | 100% | 100% |
| **合同金额识别** | 100% | 100% |
| **合同编号识别** | 0% | 0% |

**结论**：PaddleOCR + PP-StructureV3准确率更高，应作为主力方案。

---

### 4.2 成本对比

| 方案 | 成本 | 限制 |
|------|------|------|
| **PaddleOCR + PP-StructureV3** | ✅ **完全免费** | ✅ 无限制 |
| **百度OCR** | ⚠️ 有限免费 | ⚠️ 有额度限制 |

**结论**：PaddleOCR成本优势明显。

---

### 4.3 数据安全对比

| 方案 | 数据位置 | 安全性 |
|------|---------|--------|
| **PaddleOCR + PP-StructureV3** | ✅ **本地** | ✅ 高（数据不上传） |
| **百度OCR** | ⚠️ 云端 | ⚠️ 低（数据上传云端） |

**结论**：PaddleOCR数据安全性更高。

---

## 五、实施计划

### 5.1 立即实施（今天）

- [x] 确定PaddleOCR为主力方案
- [x] 明确百度OCR仅作备选
- [ ] 更新所有OCR调用代码，默认使用PaddleOCR
- [ ] 添加百度OCR使用审批逻辑

### 5.2 近期实施（本周）

- [ ] 开发智能路由模块（优先PaddleOCR）
- [ ] 建立使用日志记录
- [ ] 定期审计百度OCR使用情况

### 5.3 长期维护（持续）

- [ ] 持续优化PaddleOCR准确率
- [ ] 定期验证百度OCR作为备选的可用性
- [ ] 建立质量监控体系

---

## 六、监控与审计

### 6.1 使用统计

**每周统计**：
- PaddleOCR使用次数
- 百度OCR使用次数
- 百度OCR使用原因分析

**目标**：
- PaddleOCR使用率 ≥ 95%
- 百度OCR使用率 ≤ 5%

### 6.2 质量监控

**每日监控**：
- PaddleOCR识别准确率
- PaddleOCR服务可用性
- 识别失败案例记录

**预警阈值**：
- 准确率 < 80% → 黄色预警
- 准确率 < 70% → 红色预警
- 服务不可用 → 立即通知

---

## 七、应急预案

### 7.1 PaddleOCR服务不可用

**触发条件**：PaddleOCR服务崩溃、模型损坏、内存溢出

**应急流程**：
1. 系统自动检测到PaddleOCR不可用
2. 发送预警通知（飞书消息）
3. 临时切换到百度OCR（需要用户确认）
4. 记录使用百度OCR的原因
5. 尽快修复PaddleOCR服务

### 7.2 百度OCR额度用尽

**触发条件**：百度OCR免费额度用尽

**应急流程**：
1. 系统检测到百度OCR额度不足
2. 发送预警通知
3. 强制使用PaddleOCR（即使质量较低）
4. 加快PaddleOCR问题修复

---

## 八、总结

### 8.1 核心原则

**✅ 主力：PaddleOCR + PP-StructureV3**
- 准确率高（83.3%）
- 完全免费，无限制
- 数据安全，本地部署
- 甲乙方识别优秀（100%）

**⚠️ 备选：百度OCR**
- 仅当本地不可用时使用
- 有额度限制
- 数据上传云端
- 需要审批

### 8.2 预期效果

| 指标 | 目标 | 说明 |
|------|------|------|
| **PaddleOCR使用率** | ≥ 95% | 主力方案 |
| **百度OCR使用率** | ≤ 5% | 备选方案 |
| **综合准确率** | ≥ 83% | PaddleOCR基准 |
| **数据安全** | 100% | 本地处理 |

---

**方案确定时间**：2026-06-24 12:48  
**方案制定人**：pm-director  
**方案状态**：✅ 已确定，立即实施
