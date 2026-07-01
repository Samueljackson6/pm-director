#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科研类与服务类项目智能识别器
支持：研究阶段识别、付款计划识别、阶段与付款对应关系推断

创建日期：2026-06-26
版本：V1.0
"""

import re
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ResearchStage:
    """研究阶段"""
    stage_number: int          # 阶段编号
    stage_name: str            # 阶段名称
    research_content: str      # 研究内容
    assessment_target: str     # 考核目标
    time_node: str             # 时间节点
    start_date: Optional[str] = None  # 开始时间
    end_date: Optional[str] = None    # 结束时间


@dataclass
class PaymentPlan:
    """付款计划"""
    payment_number: int        # 付款编号
    payment_condition: str     # 付款条件
    amount: float              # 金额（元）
    amount_unit: str           # 金额单位（元/万元）
    payment_time: str          # 付款时间
    corresponding_stages: List[int] = None  # 对应阶段编号列表


@dataclass
class ServiceProjectTimeline:
    """服务类项目工期"""
    start_date: Optional[str]  # 开始时间
    end_date: Optional[str]    # 结束时间
    duration: Optional[str]    # 总工期
    duration_days: Optional[int] = None  # 工期天数
    key_milestones: List[Dict] = None  # 关键里程碑


class ContractTypeDetector:
    """合同类型检测器"""
    
    # 科研类项目关键词
    RESEARCH_KEYWORDS = [
        '研究', '研发', '科技项目', '科研项目', '课题',
        '关键技术', '核心技术研究', '技术创新', '方法研究'
    ]
    
    # 服务类项目关键词
    SERVICE_KEYWORDS = [
        '服务', '运维', '维护', '支撑', '实施',
        '建设', '改造', '升级', '供应', '采购'
    ]
    
    # 科研类项目章节关键词
    RESEARCH_CHAPTERS = [
        '研究内容', '考核目标', '项目进度安排',
        '项目支付计划', '经费预算', '研究计划'
    ]
    
    # 服务类项目章节关键词
    SERVICE_CHAPTERS = [
        '服务内容', '服务要求', '交付物',
        '工期', '完成时间', '验收标准'
    ]
    
    @staticmethod
    def detect(project_name: str, text: str) -> str:
        """
        检测合同类型
        
        Returns:
            'research': 科研类项目
            'service': 服务类项目
            'unknown': 未知类型
        """
        # 检测项目名称关键词
        research_score = sum(1 for kw in ContractTypeDetector.RESEARCH_KEYWORDS if kw in project_name)
        service_score = sum(1 for kw in ContractTypeDetector.SERVICE_KEYWORDS if kw in project_name)
        
        # 检测章节关键词
        research_score += sum(1 for kw in ContractTypeDetector.RESEARCH_CHAPTERS if kw in text)
        service_score += sum(1 for kw in ContractTypeDetector.SERVICE_CHAPTERS if kw in text)
        
        # 判断类型
        if research_score > service_score and research_score >= 2:
            return 'research'
        elif service_score > research_score and service_score >= 2:
            return 'service'
        else:
            return 'unknown'


class ResearchProjectParser:
    """科研类项目解析器"""
    
    # 阶段识别正则表达式
    STAGE_PATTERNS = [
        # 规则1：时间范围 + 主要内容/考核目标（实际OCR格式）
        r'(\d{4}年\d{1,2}月\d{1,2}日[—–-]\d{4}年\d{1,2}月\d{1,2}日)\s+主要内容[：:]\s*([^考]+?)(?=考核目标|$)',
        # 规则2：研究内容：完成XX
        r'研究内容[：:]\s*(完成[^\n]+)',
        # 规则3：第X阶段：内容
        r'第([一二三四五六七八九十\d]+)阶段[：:（\(](.+?)[）\)]?(?=[\n第]|$)',
    ]
    
    # 付款识别正则表达式
    PAYMENT_PATTERNS = [
        # 规则1：完成本合同条款5.X模式（合同9格式）
        r'(完成本合同条款5\.\d[^收]+?)\s+\d{4}年\s+[\d\.]+\s+0',
        # 规则2：年度 + 收款单位 + 付款条件 + 金额（虚拟电厂OCR表格格式）
        r'(\d{4}年)[^\d]*?(完成[^0-9\n]{5,30}?)[^\d]*?(\d+\.?\d*)\s+0\s+[^\n]*',
        # 规则3：年度 + 付款条件 + 甲方提供经费 + 金额
        r'(\d{4}年)\s+(完成[^甲]+?)\s+甲方.*?(\d+\.?\d+)\s*$',
        # 规则4：完成XX + 金额万元
        r'(完成[^\d\n]+?)\s+(\d+\.?\d*)\s*万元',
    ]
    
    # 金额单位转换
    AMOUNT_UNITS = {
        '元': 1,
        '万元': 10000,
        '万': 10000,
    }
    
    @staticmethod
    def parse_research_stages(text: str) -> List[ResearchStage]:
        """
        提取研究阶段
        
        Args:
            text: 合同文本
        
        Returns:
            研究阶段列表
        """
        stages = []
        
        # 定位"项目进度安排"章节
        stage_section = ResearchProjectParser._extract_section(text, ['项目进度安排', '研究计划', '实施计划', '研究内容'])
        
        if not stage_section:
            # 如果找不到章节，尝试全文识别
            stage_section = text
        
        # 方法1：识别"研究内容：完成XX"模式
        content_matches = re.findall(r'研究内容[：:]\s*(完成[^\n]+)', stage_section)
        
        if content_matches:
            for i, content in enumerate(content_matches, 1):
                # 提取考核目标
                target_match = re.search(rf'{re.escape(content)}[^\n]*考核目标[：:]\s*([^\n]+)', stage_section)
                target = target_match.group(1) if target_match else ""
                
                stage = ResearchStage(
                    stage_number=i,
                    stage_name=f"第{i}阶段",
                    research_content=content.strip(),
                    assessment_target=target.strip(),
                    time_node=""
                )
                stages.append(stage)
            
            return stages
        
        # 方法2：尝试不同的阶段识别规则
        for pattern in ResearchProjectParser.STAGE_PATTERNS:
            matches = re.findall(pattern, stage_section, re.MULTILINE | re.DOTALL)
            
            if matches:
                for i, match in enumerate(matches, 1):
                    if isinstance(match, tuple):
                        if len(match) >= 3:
                            # 有时间的阶段
                            stage = ResearchStage(
                                stage_number=i,
                                stage_name=f"第{i}阶段",
                                research_content=match[2] if len(match) > 2 else match[1],
                                assessment_target="",
                                time_node=match[1] if re.match(r'\d{4}年', match[1]) else ""
                            )
                        else:
                            # 普通阶段
                            stage = ResearchStage(
                                stage_number=i,
                                stage_name=f"第{i}阶段",
                                research_content=match[1] if len(match) > 1 else match[0],
                                assessment_target="",
                                time_node=""
                            )
                    else:
                        stage = ResearchStage(
                            stage_number=i,
                            stage_name=f"第{i}阶段",
                            research_content=match,
                            assessment_target="",
                            time_node=""
                        )
                    stages.append(stage)
                
                # 如果成功提取，退出循环
                if stages:
                    break
        
        return stages
    
    @staticmethod
    def parse_payment_plans(text: str) -> List[PaymentPlan]:
        """
        提取付款计划
        
        Args:
            text: 合同文本
        
        Returns:
            付款计划列表
        """
        payments = []
        
        # 定位"项目支付计划"章节
        payment_section = ResearchProjectParser._extract_section(text, ['项目支付计划', '经费预算', '付款安排', '支付计划'])
        
        if not payment_section:
            # 如果找不到章节，尝试全文识别
            payment_section = text
        
        # 提取付款信息
        lines = payment_section.split('\n')
        
        for i, line in enumerate(lines):
            # 尝试匹配付款信息
            for pattern in ResearchProjectParser.PAYMENT_PATTERNS:
                match = re.search(pattern, line)
                
                if match:
                    # 提取金额 - 取最后一个匹配组
                    groups = match.groups()
                    amount_str = groups[-1]  # 最后一组通常是金额
                    amount = float(amount_str)
                    
                    # 判断金额单位
                    if '万元' in line or '万' in line or amount < 100:  # 小于100的数字通常是万元
                        amount_unit = '万元'
                        amount_yuan = amount * 10000
                    else:
                        amount_unit = '元'
                        amount_yuan = amount
                    
                    # 提取付款条件
                    if groups[0] and re.match(r'\d{4}年', groups[0]):
                        payment_time = groups[0]
                        # 查找"完成"开头的条件
                        for g in groups[1:-1]:
                            if g and '完成' in g:
                                payment_condition = g.strip()
                                break
                        else:
                            payment_condition = groups[1] if len(groups) > 1 else ""
                    else:
                        payment_time = ""
                        # 查找"完成"开头的条件
                        for g in groups[:-1]:
                            if g and '完成' in g:
                                payment_condition = g.strip()
                                break
                        else:
                            payment_condition = groups[0] if groups[0] else ""
                    
                    # 验证：付款条件必须包含"完成"
                    if not payment_condition or '完成' not in payment_condition:
                        continue
                    
                    payment = PaymentPlan(
                        payment_number=len(payments) + 1,
                        payment_condition=payment_condition.strip(),
                        amount=amount_yuan,
                        amount_unit=amount_unit,
                        payment_time=payment_time.strip()
                    )
                    payments.append(payment)
                    break
        
        return payments
    
    @staticmethod
    def infer_stage_payment_correspondence(stages: List[ResearchStage], payments: List[PaymentPlan]) -> List[PaymentPlan]:
        """
        推断阶段与付款的对应关系
        
        Args:
            stages: 研究阶段列表
            payments: 付款计划列表
        
        Returns:
            更新后的付款计划列表（包含对应阶段信息）
        """
        for payment in payments:
            corresponding_stages = []
            
            # 优先级1：付款条件明确提及阶段
            stage_match = re.search(r'第([一二三四五六七八九十\d]+)阶段', payment.payment_condition)
            if stage_match:
                stage_num = ResearchProjectParser._chinese_to_number(stage_match.group(1))
                corresponding_stages.append(stage_num)
            
            # 优先级2：付款条件与研究内容匹配
            if not corresponding_stages:
                for stage in stages:
                    if stage.research_content in payment.payment_condition:
                        corresponding_stages.append(stage.stage_number)
            
            # 优先级3：时间节点匹配
            if not corresponding_stages and payment.payment_time:
                for stage in stages:
                    if stage.time_node and payment.payment_time[:7] in stage.time_node:
                        corresponding_stages.append(stage.stage_number)
            
            # 更新对应阶段
            payment.corresponding_stages = corresponding_stages if corresponding_stages else [0]  # 0表示未确定
        
        return payments
    
    @staticmethod
    def _extract_section(text: str, keywords: List[str]) -> str:
        """
        提取指定章节内容
        
        Args:
            text: 合同文本
            keywords: 章节关键词列表
        
        Returns:
            章节内容
        """
        for keyword in keywords:
            # 查找章节标题
            pattern = rf'{keyword}[^\n]*\n'
            match = re.search(pattern, text)
            
            if match:
                # 提取章节内容（到下一个章节标题或文档结束）
                start = match.end()
                end_match = re.search(r'\n\d+\.[^\n]*\n', text[start:])
                
                if end_match:
                    end = start + end_match.start()
                else:
                    end = len(text)
                
                return text[start:end].strip()
        
        return ""
    
    @staticmethod
    def _chinese_to_number(chinese: str) -> int:
        """
        中文数字转阿拉伯数字
        
        Args:
            chinese: 中文数字（一、二、三...）
        
        Returns:
            阿拉伯数字
        """
        mapping = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
        }
        return mapping.get(chinese, int(chinese) if chinese.isdigit() else 0)


class ServiceProjectParser:
    """服务类项目解析器"""
    
    # 工期识别正则表达式
    DURATION_PATTERNS = [
        # 规则1：工期X天
        r'工期[：:]\s*(\d+)\s*天',
        # 规则2：X日内完成
        r'(\d+)\s*日[内内]完成',
        # 规则3：时间范围
        r'(\d{4}年\d{1,2}月\d{1,2}日)[至到~](\d{4}年\d{1,2}月\d{1,2}日)',
        # 规则4：截止日期
        r'在[？]?(\d{4}年\d{1,2}月\d{1,2}日)[之前]?完成',
    ]
    
    @staticmethod
    def parse_timeline(text: str) -> ServiceProjectTimeline:
        """
        提取工期信息
        
        Args:
            text: 合同文本
        
        Returns:
            工期信息
        """
        timeline = ServiceProjectTimeline(
            start_date=None,
            end_date=None,
            duration=None,
            duration_days=None,
            key_milestones=[]
        )
        
        # 定位"工期"章节
        duration_section = ServiceProjectParser._extract_section(text, ['工期', '服务期限', '合同期限', '项目周期'])
        
        if not duration_section:
            return timeline
        
        # 尝试匹配工期信息
        for pattern in ServiceProjectParser.DURATION_PATTERNS:
            match = re.search(pattern, duration_section)
            
            if match:
                # 规则1：工期X天
                if '天' in pattern:
                    duration_days = int(match.group(1))
                    timeline.duration = f"{duration_days}天"
                    timeline.duration_days = duration_days
                
                # 规则2：X日内完成
                elif '日内完成' in pattern:
                    duration_days = int(match.group(1))
                    timeline.duration = f"{duration_days}天"
                    timeline.duration_days = duration_days
                
                # 规则3：时间范围
                elif '至' in pattern or '到' in pattern or '~' in pattern:
                    start_date = ServiceProjectParser._normalize_date(match.group(1))
                    end_date = ServiceProjectParser._normalize_date(match.group(2))
                    timeline.start_date = start_date
                    timeline.end_date = end_date
                
                # 规则4：截止日期
                elif '之前完成' in pattern or '前完成' in pattern:
                    end_date = ServiceProjectParser._normalize_date(match.group(1))
                    timeline.end_date = end_date
                
                # 如果成功提取，退出循环
                break
        
        return timeline
    
    @staticmethod
    def _extract_section(text: str, keywords: List[str]) -> str:
        """
        提取指定章节内容
        """
        for keyword in keywords:
            pattern = rf'{keyword}[^\n]*\n'
            match = re.search(pattern, text)
            
            if match:
                start = match.end()
                end_match = re.search(r'\n\d+\.[^\n]*\n', text[start:])
                
                if end_match:
                    end = start + end_match.start()
                else:
                    end = len(text)
                
                return text[start:end].strip()
        
        return ""
    
    @staticmethod
    def _normalize_date(date_str: str) -> str:
        """
        标准化日期格式
        
        Args:
            date_str: 日期字符串
        
        Returns:
            标准日期格式（YYYY-MM-DD）
        """
        # 提取年月日
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
        
        if match:
            year = match.group(1)
            month = match.group(2).zfill(2)
            day = match.group(3).zfill(2)
            return f"{year}-{month}-{day}"
        
        return date_str


class ContractIntelligentRecognizer:
    """合同智能识别器"""
    
    def __init__(self):
        self.type_detector = ContractTypeDetector()
        self.research_parser = ResearchProjectParser()
        self.service_parser = ServiceProjectParser()
    
    def recognize(self, project_name: str, text: str) -> Dict:
        """
        智能识别合同信息
        
        Args:
            project_name: 项目名称
            text: 合同文本
        
        Returns:
            识别结果
        """
        result = {
            'project_name': project_name,
            'project_type': 'unknown',
            'research_stages': [],
            'payment_plans': [],
            'service_timeline': None,
            'correspondence_matrix': []
        }
        
        # 检测合同类型
        contract_type = self.type_detector.detect(project_name, text)
        result['project_type'] = contract_type
        
        # 根据类型解析
        if contract_type == 'research':
            # 提取研究阶段
            stages = self.research_parser.parse_research_stages(text)
            result['research_stages'] = [asdict(s) for s in stages]
            
            # 提取付款计划
            payments = self.research_parser.parse_payment_plans(text)
            
            # 推断对应关系
            payments = self.research_parser.infer_stage_payment_correspondence(stages, payments)
            result['payment_plans'] = [asdict(p) for p in payments]
            
            # 生成对应关系矩阵
            result['correspondence_matrix'] = self._build_correspondence_matrix(stages, payments)
        
        elif contract_type == 'service':
            # 提取工期信息
            timeline = self.service_parser.parse_timeline(text)
            result['service_timeline'] = asdict(timeline)
        
        return result
    
    @staticmethod
    def _build_correspondence_matrix(stages: List[ResearchStage], payments: List[PaymentPlan]) -> List[Dict]:
        """
        构建阶段与付款的对应关系矩阵
        
        Args:
            stages: 研究阶段列表
            payments: 付款计划列表
        
        Returns:
            对应关系矩阵
        """
        matrix = []
        
        for payment in payments:
            for stage_num in payment.corresponding_stages:
                # 查找对应的阶段
                stage = next((s for s in stages if s.stage_number == stage_num), None)
                
                if stage:
                    matrix.append({
                        'stage_number': stage_num,
                        'stage_name': stage.stage_name,
                        'research_content': stage.research_content,
                        'payment_number': payment.payment_number,
                        'payment_condition': payment.payment_condition,
                        'amount': payment.amount,
                        'amount_unit': payment.amount_unit,
                        'correspondence_type': '1:1' if len(payment.corresponding_stages) == 1 else 'N:1'
                    })
        
        return matrix


def main():
    """测试函数"""
    # 测试案例
    test_text = """
    项目名称：新型电力系统背景下虚拟电厂规划及运行优化研究
    
    一、项目进度安排
    
    第一阶段：完成项目研究实施方案
    研究内容：编写项目研究实施方案
    考核目标：通过专家评审
    
    第二阶段：完成1份专利申请
    研究内容：开展专利申请工作
    考核目标：获得专利受理通知书
    
    二、项目支付计划
    
    2024年  完成项目研究实施方案  18.03万元
    2024年  完成1份专利申请  18.03万元
    """
    
    recognizer = ContractIntelligentRecognizer()
    result = recognizer.recognize("新型电力系统背景下虚拟电厂规划及运行优化研究", test_text)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
