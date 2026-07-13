#!/bin/bash
# 知识库搜索脚本
# 用法: ./scripts/search-knowledge.sh "关键词"

KNOWLEDGE_BASE="knowledge-base"
DOCS="docs"
AUDITS="docs/audits"

if [ -z "$1" ]; then
    echo "用法: $0 \"关键词\""
    echo "示例: $0 \"路由\""
    exit 1
fi

KEYWORD="$1"

echo "=========================================="
echo "搜索知识库: $KEYWORD"
echo "=========================================="

echo ""
echo "📂 知识库:"
echo "----------------------------------------"
grep -rn --color=always "$KEYWORD" "$KNOWLEDGE_BASE" 2>/dev/null || echo "未找到"

echo ""
echo "📂 规范文档:"
echo "----------------------------------------"
grep -rn --color=always "$KEYWORD" "$DOCS" --include="*.md" 2>/dev/null | grep -v audits || echo "未找到"

echo ""
echo "📂 审计报告:"
echo "----------------------------------------"
grep -rn --color=always "$KEYWORD" "$AUDITS" 2>/dev/null || echo "未找到"

echo ""
echo "=========================================="
echo "搜索完成"
echo "=========================================="
