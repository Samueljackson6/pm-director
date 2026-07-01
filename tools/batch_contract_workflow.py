#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合同批量识别工作流
自动化识别 + 人工校验

使用方法：
1. 准备PDF文件到 /tmp/contracts/
2. 运行PP-StructureV3识别（每个PDF需要5-30分钟）
3. 运行本脚本进行智能识别
4. 人工校验识别结果
5. 保存到缓存
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/home/samuel/.openclaw/workspace/pm-director/tools')

from contract_cache_manager import ContractCacheManager
from contract_intelligent_recognizer import ContractIntelligentRecognizer


class ContractBatchWorkflow:
    """合同批量识别工作流"""
    
    def __init__(self):
        self.cache_mgr = ContractCacheManager()
        self.recognizer = ContractIntelligentRecognizer()
        self.results = []
        self.errors = []
    
    def extract_text_from_ocr(self, ocr_file):
        """从OCR结果提取文本"""
        with open(ocr_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        all_texts = []
        for i, page in enumerate(results, 1):
            if 'overall_ocr_res' in page and page['overall_ocr_res']:
                ocr_res = page['overall_ocr_res']
                if 'rec_texts' in ocr_res and ocr_res['rec_texts']:
                    texts = ocr_res['rec_texts']
                    page_text = ' '.join(texts)
                    all_texts.append(f'[第{i}页]\n{page_text}')
        
        return '\n\n'.join(all_texts)
    
    def process_contract(self, pdf_path, ocr_path=None, contract_name=None):
        """
        处理单个合同
        
        Args:
            pdf_path: PDF文件路径
            ocr_path: OCR结果文件路径（可选）
            contract_name: 合同名称（可选）
        
        Returns:
            识别结果
        """
        contract_name = contract_name or Path(pdf_path).stem
        
        print(f"\n{'='*80}")
        print(f"处理合同: {contract_name}")
        print(f"{'='*80}")
        
        # 检查缓存
        cached = self.cache_mgr.get_cache(pdf_path)
        if cached:
            print(f"✅ 从缓存读取")
            return cached['recognized']
        
        # 检查OCR结果
        if not ocr_path or not os.path.exists(ocr_path):
            print(f"⚠️ 无OCR结果，需要先运行PP-StructureV3识别")
            self.errors.append({
                'name': contract_name,
                'path': pdf_path,
                'error': 'No OCR result'
            })
            return None
        
        # 提取文本
        print(f"步骤1：提取OCR文本...")
        text = self.extract_text_from_ocr(ocr_path)
        print(f"✅ 提取文本: {len(text)}个字符")
        
        # 智能识别
        print(f"\n步骤2：智能识别...")
        result = self.recognizer.recognize(contract_name, text)
        
        print(f"\n识别结果:")
        print(f"  合同类型: {result['project_type']}")
        print(f"  研究阶段: {len(result['research_stages'])}个")
        print(f"  付款计划: {len(result['payment_plans'])}笔")
        
        # 保存到缓存
        print(f"\n步骤3：保存到缓存...")
        with open(ocr_path, 'r', encoding='utf-8') as f:
            ocr_result = json.load(f)
        
        self.cache_mgr.save_cache(pdf_path, text, result, ocr_result)
        print(f"✅ 已保存到缓存")
        
        self.results.append({
            'name': contract_name,
            'result': result
        })
        
        return result
    
    def process_all_contracts(self, contract_list):
        """
        批量处理合同
        
        Args:
            contract_list: 合同列表 [{'pdf': '...', 'ocr': '...', 'name': '...'}, ...]
        """
        print("=" * 80)
        print("批量合同识别工作流")
        print("=" * 80)
        print(f"待处理合同数: {len(contract_list)}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for i, contract in enumerate(contract_list, 1):
            print(f"\n[{i}/{len(contract_list)}]")
            self.process_contract(
                pdf_path=contract['pdf'],
                ocr_path=contract.get('ocr'),
                contract_name=contract.get('name')
            )
        
        # 输出统计
        print("\n" + "=" * 80)
        print("识别完成统计")
        print("=" * 80)
        print(f"成功: {len(self.results)}个")
        print(f"失败: {len(self.errors)}个")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存错误日志
        if self.errors:
            with open('/tmp/batch_recognition_errors.json', 'w', encoding='utf-8') as f:
                json.dump(self.errors, f, ensure_ascii=False, indent=2)
            print(f"\n错误日志: /tmp/batch_recognition_errors.json")


def main():
    """主函数 - 示例用法"""
    
    workflow = ContractBatchWorkflow()
    
    # 已有OCR结果的合同
    contracts_with_ocr = [
        {
            'pdf': '/tmp/contracts/合同9-断面限额语义识别.pdf',
            'ocr': '/tmp/contract_9_result.json',
            'name': '合同9-断面限额语义识别'
        },
    ]
    
    # 待OCR的合同（需要先运行PP-StructureV3）
    contracts_need_ocr = [
        {'pdf': '/tmp/contracts/合同10-川西高原冻融区域排查.pdf', 'name': '合同10-川西高原冻融'},
        {'pdf': '/tmp/contracts/合同11-自贡富顺水电站大坝形变观测.pdf', 'name': '合同11-自贡富顺'},
        {'pdf': '/tmp/contracts/合同1-雅安花滩电站大坝观测.pdf', 'name': '合同1-雅安花滩'},
    ]
    
    print("=" * 80)
    print("合同批量识别工作流指南")
    print("=" * 80)
    
    print("\n阶段1：处理已有OCR结果的合同")
    print(f"  数量: {len(contracts_with_ocr)}个")
    
    print("\n阶段2：对其他合同运行PP-StructureV3识别")
    print(f"  数量: {len(contracts_need_ocr)}个")
    print("  命令示例:")
    for c in contracts_need_ocr:
        print(f"    python3 tools/pp_structure_recognize.py {c['pdf']}")
    
    print("\n阶段3：识别所有合同")
    print("  运行: python3 tools/batch_contract_workflow.py --all")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
