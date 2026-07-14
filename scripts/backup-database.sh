#!/bin/bash
# ============================================================
# SQLite 数据库备份脚本
# 对应 Issue: T13
# 用法: bash scripts/backup-database.sh [--daily|--weekly]
# ============================================================

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DB_PATH="$PROJECT_ROOT/database/project_management.db"
BACKUP_DIR="$PROJECT_ROOT/database/backups"
LOG_FILE="$BACKUP_DIR/backup.log"
MAX_DAILY_BACKUPS=7
MAX_WEEKLY_BACKUPS=4

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份类型
BACKUP_TYPE="${1:-daily}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

if [ "$BACKUP_TYPE" = "--weekly" ]; then
    BACKUP_NAME="weekly-$TIMESTAMP.db"
else
    BACKUP_NAME="daily-$TIMESTAMP.db"
fi

BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# 检查数据库是否存在
if [ ! -f "$DB_PATH" ]; then
    echo "[$(date)] ERROR: 数据库文件不存在: $DB_PATH" | tee -a "$LOG_FILE"
    exit 1
fi

# 执行备份
echo "[$(date)] 开始备份: $BACKUP_NAME" | tee -a "$LOG_FILE"
cp "$DB_PATH" "$BACKUP_PATH"

# 计算校验和
SHA256=$(sha256sum "$BACKUP_PATH" | cut -d' ' -f1)
echo "$SHA256  $BACKUP_NAME" > "$BACKUP_DIR/sha256-$TIMESTAMP.txt"

# 验证备份
if [ -f "$BACKUP_PATH" ]; then
    BACKUP_SIZE=$(stat -c%s "$BACKUP_PATH" 2>/dev/null || stat -f%z "$BACKUP_PATH")
    ORIGINAL_SIZE=$(stat -c%s "$DB_PATH" 2>/dev/null || stat -f%z "$DB_PATH")
    if [ "$BACKUP_SIZE" = "$ORIGINAL_SIZE" ]; then
        echo "[$(date)] 备份成功: $BACKUP_PATH (${BACKUP_SIZE} bytes, SHA256: ${SHA256:0:16}...)" | tee -a "$LOG_FILE"
    else
        echo "[$(date)] WARNING: 备份大小不一致 (原: $ORIGINAL_SIZE, 备份: $BACKUP_SIZE)" | tee -a "$LOG_FILE"
    fi
else
    echo "[$(date)] ERROR: 备份文件创建失败" | tee -a "$LOG_FILE"
    exit 1
fi

# 清理旧备份
if [ "$BACKUP_TYPE" = "--weekly" ]; then
    # 保留最近 4 个周备份
    cd "$BACKUP_DIR"
    ls -t weekly-*.db 2>/dev/null | tail -n +$((MAX_WEEKLY_BACKUPS + 1)) | xargs -r rm -f
    echo "[$(date)] 清理旧周备份，保留最近 $MAX_WEEKLY_BACKUPS 个" | tee -a "$LOG_FILE"
else
    # 保留最近 7 个日备份
    cd "$BACKUP_DIR"
    ls -t daily-*.db 2>/dev/null | tail -n +$((MAX_DAILY_BACKUPS + 1)) | xargs -r rm -f
    echo "[$(date)] 清理旧日备份，保留最近 $MAX_DAILY_BACKUPS 个" | tee -a "$LOG_FILE"
fi

# 更新备份日志
echo "[$(date)] 备份完成: $BACKUP_NAME" >> "$BACKUP_DIR/BACKUP-LOG.md"

echo ""
echo "=== 备份摘要 ==="
echo "文件: $BACKUP_PATH"
echo "大小: $BACKUP_SIZE bytes"
echo "SHA256: $SHA256"
echo "类型: $BACKUP_TYPE"
