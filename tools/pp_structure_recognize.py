#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PP-StructureV3 合同识别工具 - 正确版本
修复：使用predict()方法而非直接调用对象
"""

import sys
import json
from pathlib import Path

# 检查环境
try:
    from paddleocr import PPStructureV3
    PADDLEOCR_AVAILABLE = True
except ImportError:
    print("❌ PaddleOCR未安装")
    sys.exit(1)

def recognize_contract_fast(pdf_path, max_pages=3):
    """
    快速识别合同PDF（仅识别前几页）
    
    Args:
        pdf_path: 合同PDF文件路径
        max_pages: 最大识别页数（默认3页，加快速度）
    
    Returns:
        dict: 识别结果
    """
    print(f"识别合同: {pdf_path}")
    
    # 初始化（模型已下载）
    print("初始化PP-StructureV3...")
    engine = PPStructureV3()
    print("✅ 初始化完成")
    
    # 使用predict()方法（正确方式）
    print(f"识别前{max_pages}页...")
    result = engine.predict(pdf_path, page_num=max_pages)
    
    print(f"✅ 完成，共{len(result)}页")
    
    # 提取关键字段（简化版）
    extracted = {
        "文件": str(pdf_path),
        "页数": len(result),
        "检测区域": []
    }
    
    # 提取第一页的关键信息
    if len(result) > 0:
        page1 = result[0]
        if 'layout_det_res' in page1:
            boxes = page1['layout_det_res'].get('boxes', [])
            for box in boxes[:10]:  # 前10个区域
                extracted["检测区域"].append({
                    "类型": box.get('label', 'unknown'),
                    "置信度": box.get('score', 0),
                    "坐标": box.get('coordinate', [])
                })
    
    return extracted

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用: python3 pp_structure_recognize.py <PDF路径> [最大页数]")
        print("示例: python3 pp_structure_recognize.py /tmp/contract.pdf 2")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    result = recognize_contract_fast(pdf_path, max_pages)
    
    # 保存结果
    output_file = f"/tmp/{Path(pdf_path).stem}_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存: {output_file}")
    print(json.dumps(result, ensure_ascii=False, indent=2))