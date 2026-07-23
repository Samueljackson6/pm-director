@echo off
REM SQLite 数据库备份脚本 - Windows 定时任务调用
REM 用法: schtasks /create /tn "PM-Director DB Backup" /tr "D:\Tare-workspace\pm-director\scripts\backup-database.bat" /sc daily /st 02:00

cd /d D:\Tare-workspace\pm-director
python scripts\backup-database.py backup >> database\backups\backup.log 2>&1
echo %date% %time% - Backup completed >> database\backups\backup.log
