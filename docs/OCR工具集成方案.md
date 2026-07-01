# OCR工具集成方案

> **目标**：将PaddleOCR集成到OpenClaw，让所有Agent都能使用OCR能力
> **创建时间**：2026-06-23 18:05
> **创建人**：pm-director

---

## 一、集成架构

### 1. 全局工具位置

```
/home/samuel/.openclaw/workspace/
└── shared-tools/
    └── ocr/
        ├── ocr_tool.py          # OCR主程序
        ├── requirements.txt      # 依赖列表
        └── README.md            # 使用说明
```

### 2. 虚拟环境

```
/home/samuel/.openclaw/workspace/pm-director/ocr-env/
```

**激活方式**：
```bash
source /home/samuel/.openclaw/workspace/pm-director/ocr-env/bin/activate
```

---

## 二、使用方式

### 方式1：直接调用脚本

```bash
source /home/samuel/.openclaw/workspace/pm-director/ocr-env/bin/activate
python /home/samuel/.openclaw/workspace/pm-director/tools/ocr_tool.py <PDF文件路径>
```

### 方式2：作为Python模块导入

```python
import sys
sys.path.append('/home/samuel/.openclaw/workspace/pm-director/tools')

from ocr_tool import ContractOCR

ocr = ContractOCR()
info = ocr.extract_contract_info(pdf_path)
```

### 方式3：封装为OpenClaw工具（待实现）

```python
# 未来可以封装为OpenClaw内置工具
from openclaw.tools import ocr

result = ocr.recognize_contract(pdf_path)
```

---

## 三、Agent调用示例

### pm-director调用

```python
# 在pm-director中使用
import subprocess
import json

def ocr_contract(pdf_path):
    """识别合同"""
    cmd = f"""
    source /home/samuel/.openclaw/workspace/pm-director/ocr-env/bin/activate && \
    python /home/samuel/.openclaw/workspace/pm-director/tools/ocr_tool.py {pdf_path}
    """

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # 读取JSON结果
    json_file = pdf_path.replace('.pdf', '_ocr_info.json')
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)
```

### 其他Agent调用

```python
# 任何Agent都可以使用相同方式调用
# 只需要知道虚拟环境和工具路径即可
```

---

## 四、测试计划

### 测试1：单个合同识别

```bash
source /home/samuel/.openclaw/workspace/pm-director/ocr-env/bin/activate
python /home/samuel/.openclaw/workspace/pm-director/tools/ocr_tool.py \
  /path/to/contract.pdf
```

**预期结果**：
- ✅ 输出合同编号、金额、日期等关键信息
- ✅ 生成OCR结果文本文件
- ✅ 生成结构化JSON文件

---

### 测试2：批量合同识别

```bash
for pdf in /path/to/contracts/*.pdf; do
  python ocr_tool.py "$pdf"
done
```

---

### 测试3：准确率验证

识别前15-20个合同，验证：
- 合同编号识别准确率
- 金额识别准确率
- 日期识别准确率
- 甲乙方信息准确率

---

## 五、优化方向

### 1. 性能优化

- GPU加速（如果有GPU）
- 批量识别优化
- 模型缓存

### 2. 准确率优化

- 图像预处理
- 自定义词典
- 规则引擎增强

### 3. 功能扩展

- 表格识别
- 印章识别
- 签名识别
- 手写体识别

---

## 六、维护说明

### 依赖更新

```bash
source ocr-env/bin/activate
pip install --upgrade paddlepaddle paddleocr
```

### 模型更新

```bash
# PaddleOCR会自动下载最新模型
# 模型存储在: ~/.paddleocr/
```

---

*创建时间：2026-06-23 18:05*
