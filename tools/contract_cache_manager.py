#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合同识别缓存管理器
避免重复识别PDF，节省时间和算力

创建日期：2026-06-26
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple


class ContractCacheManager:
    """合同识别缓存管理器"""
    
    def __init__(self, cache_dir: str = None):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录，默认 ~/.openclaw/workspace/pm-director/cache/contracts/
        """
        if cache_dir is None:
            cache_dir = Path.home() / '.openclaw' / 'workspace' / 'pm-director' / 'cache' / 'contracts'
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.cache_dir / 'index.json'
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """加载缓存索引"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        """保存缓存索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def _compute_file_hash(self, file_path: str) -> str:
        """
        计算文件哈希值
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件哈希值（MD5）
        """
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def get_cache(self, pdf_path: str) -> Optional[Dict]:
        """
        获取缓存的识别结果
        
        Args:
            pdf_path: PDF文件路径
        
        Returns:
            缓存结果（包含text和recognized），如果没有缓存则返回None
        """
        pdf_hash = self._compute_file_hash(pdf_path)
        
        if pdf_hash not in self.index:
            return None
        
        cache_info = self.index[pdf_hash]
        
        # 检查缓存文件是否存在
        text_file = self.cache_dir / cache_info['text_file']
        recognized_file = self.cache_dir / cache_info['recognized_file']
        
        if not text_file.exists() or not recognized_file.exists():
            # 缓存文件丢失，删除索引
            del self.index[pdf_hash]
            self._save_index()
            return None
        
        # 读取缓存
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        with open(recognized_file, 'r', encoding='utf-8') as f:
            recognized = json.load(f)
        
        return {
            'text': text,
            'recognized': recognized,
            'cache_time': cache_info['cache_time']
        }
    
    def save_cache(self, pdf_path: str, text: str, recognized: Dict, ocr_result: Dict = None):
        """
        保存识别结果到缓存
        
        Args:
            pdf_path: PDF文件路径
            text: 提取的文本
            recognized: 智能识别结果
            ocr_result: OCR识别结果（可选）
        """
        pdf_hash = self._compute_file_hash(pdf_path)
        
        # 生成缓存文件名
        text_file = f"{pdf_hash}_text.txt"
        recognized_file = f"{pdf_hash}_recognized.json"
        ocr_file = f"{pdf_hash}_ocr.json"
        
        # 保存文本
        text_path = self.cache_dir / text_file
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # 保存识别结果
        recognized_path = self.cache_dir / recognized_file
        with open(recognized_path, 'w', encoding='utf-8') as f:
            json.dump(recognized, f, ensure_ascii=False, indent=2)
        
        # 保存OCR结果（可选）
        if ocr_result:
            ocr_path = self.cache_dir / ocr_file
            with open(ocr_path, 'w', encoding='utf-8') as f:
                json.dump(ocr_result, f, ensure_ascii=False, indent=2, default=str)
        
        # 更新索引
        self.index[pdf_hash] = {
            'pdf_path': str(pdf_path),
            'pdf_hash': pdf_hash,
            'text_file': text_file,
            'recognized_file': recognized_file,
            'ocr_file': ocr_file if ocr_result else None,
            'cache_time': datetime.now().isoformat()
        }
        
        self._save_index()
        
        print(f"✅ 缓存已保存: {pdf_hash}")
        print(f"   文本文件: {text_file}")
        print(f"   识别结果: {recognized_file}")
    
    def list_cache(self) -> Dict:
        """列出所有缓存"""
        return self.index
    
    def clear_cache(self, pdf_path: str = None):
        """
        清除缓存
        
        Args:
            pdf_path: 指定PDF路径，如果为None则清除所有缓存
        """
        if pdf_path:
            pdf_hash = self._compute_file_hash(pdf_path)
            if pdf_hash in self.index:
                cache_info = self.index[pdf_hash]
                
                # 删除缓存文件
                for file_key in ['text_file', 'recognized_file', 'ocr_file']:
                    if file_key in cache_info and cache_info[file_key]:
                        cache_file = self.cache_dir / cache_info[file_key]
                        if cache_file.exists():
                            cache_file.unlink()
                
                # 删除索引
                del self.index[pdf_hash]
                self._save_index()
                print(f"✅ 已清除缓存: {pdf_hash}")
        else:
            # 清除所有缓存
            for cache_file in self.cache_dir.glob('*'):
                if cache_file.is_file():
                    cache_file.unlink()
            
            self.index = {}
            self._save_index()
            print("✅ 已清除所有缓存")


def main():
    """测试缓存管理器"""
    cache_mgr = ContractCacheManager()
    
    print("缓存管理器测试")
    print("=" * 80)
    
    # 测试缓存索引
    print(f"\n缓存目录: {cache_mgr.cache_dir}")
    print(f"缓存索引: {cache_mgr.index_file}")
    
    # 列出已有缓存
    index = cache_mgr.list_cache()
    if index:
        print(f"\n已有缓存: {len(index)}个")
        for pdf_hash, info in index.items():
            print(f"  {pdf_hash}: {info['pdf_path']}")
    else:
        print("\n暂无缓存")


if __name__ == '__main__':
    main()
