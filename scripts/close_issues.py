# -*- coding: utf-8 -*-
"""批量关闭已完成的 GitHub Issues"""
import subprocess
import json

REPO = "Samueljackson6/pm-director"
closed_issues = [46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56]

comments = {
    46: "[EPIC] 核心业务整改主计划",
    47: "P0-0 运行基线、构建与发布可追溯",
    48: "P0-1 数据真值、金额单位与关系契约",
    49: "P0-2 核心关系服务与财务API契约",
    50: "P0-3 合同详情页面业务闭环",
    51: "P0-4 客户发票回款及附件闭环",
    52: "P0-5 质量门禁、回归测试和Gate",
    53: "P1-1 供应商发票业务闭环",
    54: "P1-2 供应商付款业务闭环",
    55: "P1-3 台账列表统一Header",
    56: "P1-4 历史数据补录与持续数据质量监控",
}

for issue_num in closed_issues:
    title = comments.get(issue_num, f"Issue #{issue_num}")
    
    # 先检查是否已关闭
    check = subprocess.run(
        ["gh", "issue", "view", str(issue_num), "--repo", REPO, "--json", "state"],
        capture_output=True, text=True
    )
    if '"closed"' in check.stdout:
        print(f"[SKIP] #{issue_num}: already closed - {title[:50]}")
        continue
    
    # 关闭
    result = subprocess.run(
        ["gh", "issue", "close", str(issue_num), "--repo", REPO],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print(f"[CLOSED] #{issue_num}: {title[:50]}")
    else:
        print(f"[ERROR] #{issue_num}: {result.stderr[:200]}")
