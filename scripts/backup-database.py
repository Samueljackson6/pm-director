# -*- coding: utf-8 -*-
"""SQLite 数据库自动备份脚本 - 每日定时执行"""
import sqlite3
import shutil
import os
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = r'D:\Tare-workspace\pm-director\database\project_management.db'
BACKUP_DIR = r'D:\Tare-workspace\pm-director\database\backups'
RETENTION_DAYS = 30

def backup():
    """执行数据库备份"""
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found: {DB_PATH}")
        return False
    
    # 创建备份目录
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'project_management_{timestamp}.db')
    
    # 执行备份（先关闭连接，再复制）
    try:
        # 用 WAL 模式备份（如果支持）
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        conn.close()
        
        shutil.copy2(DB_PATH, backup_file)
        file_size = os.path.getsize(backup_file) / 1024 / 1024
        print(f"BACKUP OK: {backup_file} ({file_size:.2f} MB)")
        return True
    except Exception as e:
        print(f"BACKUP ERROR: {e}")
        return False

def cleanup_old_backups():
    """清理过期备份"""
    if not os.path.exists(BACKUP_DIR):
        return
    
    cutoff = datetime.now() - __import__('datetime').timedelta(days=RETENTION_DAYS)
    cleaned = 0
    
    for f in os.listdir(BACKUP_DIR):
        if f.startswith('project_management_') and f.endswith('.db'):
            filepath = os.path.join(BACKUP_DIR, f)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_mtime < cutoff:
                os.remove(filepath)
                cleaned += 1
    
    if cleaned > 0:
        print(f"CLEANUP: Removed {cleaned} old backup(s)")

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'backup'
    
    if mode == 'backup':
        success = backup()
        cleanup_old_backups()
        sys.exit(0 if success else 1)
    elif mode == 'cleanup':
        cleanup_old_backups()
    elif mode == 'restore':
        if len(sys.argv) < 3:
            print("Usage: backup-db.py restore <backup-file>")
            sys.exit(1)
        backup_file = sys.argv[2]
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, DB_PATH)
            print(f"RESTORE: {backup_file} -> {DB_PATH}")
        else:
            print(f"ERROR: Backup file not found: {backup_file}")
            sys.exit(1)
