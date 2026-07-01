# API容错机制设计

> **创建时间**：2026-06-24  
> **维护人**：pm-director

---

## 一、容错机制目标

**核心目标**：API调用失败时，仍能完成合同入库工作

**关键指标**：
- 容错成功率：≥ 95%
- 数据丢失率：0%
- 人工干预率：≤ 20%

---

## 二、容错策略

### 2.1 三层容错架构

```
第一层：API自动调用
  ↓ 失败
第二层：本地缓存 + 稍后重试
  ↓ 失败
第三层：手动操作 + 人工审核
```

---

### 2.2 具体容错措施

#### 措施1：API调用失败自动记录

**实现方式**：
```python
def call_api_with_fallback(api_func, data, log_file):
    try:
        result = api_func(data)
        return {"success": True, "data": result}
    except Exception as e:
        # 记录失败请求
        with open(log_file, 'a') as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "api": api_func.__name__,
                "data": data,
                "error": str(e)
            }))
        return {"success": False, "error": str(e)}
```

---

#### 措施2：本地缓存机制

**实现方式**：
- 所有关键数据保存到本地JSON文件
- 文件路径：`/tmp/contracts/contract_XX_fill_data.json`
- 定期同步到飞书（API恢复后）

---

#### 措施3：批量重试机制

**触发条件**：API恢复后或定时任务

**实现方式**：
```python
def batch_retry_failed_operations(log_file):
    with open(log_file, 'r') as f:
        failed_ops = [json.loads(line) for line in f]
    
    success_count = 0
    for op in failed_ops:
        try:
            result = call_api(op['api'], op['data'])
            success_count += 1
        except:
            pass
    
    return {"total": len(failed_ops), "success": success_count}
```

---

#### 措施4：人工操作清单

**场景**：API长时间不可用

**实现方式**：
1. 生成人工操作清单（Excel格式）
2. 列出待填充的合同和字段
3. 提供填充指南和示例
4. 人工完成后导入飞书

---

## 三、容错流程图

```
开始合同入库
    ↓
尝试API调用
    ↓
成功？ ──Yes→ 完成
    ↓No
记录失败请求
    ↓
保存到本地缓存
    ↓
加入重试队列
    ↓
定期重试
    ↓
成功？ ──Yes→ 同步到飞书
    ↓No
生成人工操作清单
    ↓
人工填充
    ↓
验证数据
    ↓
完成
```

---

## 四、应急预案

### 4.1 API完全不可用

**预案**：
1. 全部使用本地缓存
2. 生成Excel批量导入模板
3. 人工批量导入飞书

**时间**：每批次30分钟

---

### 4.2 API部分可用

**预案**：
1. 可用的API正常调用
2. 不可用的API使用本地缓存
3. 混合模式运行

**时间**：实时处理

---

### 4.3 数据冲突处理

**场景**：本地缓存与飞书数据不一致

**预案**：
1. 以飞书数据为准
2. 人工审核差异
3. 合并或覆盖

---

## 五、监控与报警

### 5.1 监控指标

| 指标 | 阈值 | 报警级别 |
|------|------|---------|
| API失败率 | > 10% | 🟡 警告 |
| API失败率 | > 30% | 🟠 严重 |
| API失败率 | > 50% | 🔴 紧急 |
| 本地缓存大小 | > 100条 | 🟡 警告 |

---

### 5.2 报警方式

- 自动发送消息到pm-director
- 记录到日志文件
- 生成报告文档

---

## 六、容错测试

### 6.1 测试场景

1. 模拟API超时
2. 模拟API返回错误
3. 模拟网络中断
4. 模拟权限不足

### 6.2 验证标准

- ✅ 数据不丢失
- ✅ 操作可追溯
- ✅ 可恢复执行

---

**维护说明**：
- 每月检查容错机制有效性
- 每季度优化容错策略
- 定期清理过期的本地缓存
