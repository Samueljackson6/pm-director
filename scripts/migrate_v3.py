#!/usr/bin/env python3
"""
v3.0 Database Migration — "合同+项目"双核模型

Phase 0: 数据模型搭建
- 创建 6 张新表 (projects, contract_project_link, contract_files,
  personnel, project_personnel, payment_vouchers)
- 扩展 contracts 表 (7 个新字段)
- 扩展 stages / payments / deliverables (project_id 关联)
- 初始化 50 个 project 记录 (1:1 复用 contract_id)
- 回填 stages/payments/deliverables 的 project_id

用法:
    python scripts/migrate_v3.py          # 执行迁移
    python scripts/migrate_v3.py --dry-run # 仅打印 SQL，不执行

安全: 幂等 (CREATE IF NOT EXISTS / 列存在检查 / 无数据删除)
"""

import sqlite3
import sys
from pathlib import Path

# ─── 路径 ─────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DB_PATH = PROJECT_ROOT / "database" / "project_management.db"


# ─── 工具函数 ─────────────────────────────────────────────────────────────

def column_exists(cur: sqlite3.Cursor, table: str, col: str) -> bool:
    """检查表中是否存在某列 (SQLite PRAGMA table_info)"""
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == col for row in cur.fetchall())


def log(msg: str, dry_run: bool = False):
    prefix = "[DRY-RUN] " if dry_run else ""
    print(f"{prefix}{msg}")


# ═══════════════════════════════════════════════════════════════════════════
#  SQL 构建
# ═══════════════════════════════════════════════════════════════════════════

def build_sql_plan() -> list[tuple[str, str, callable]]:
    """
    返回 [(step_label, sql_or_placeholder, callback_or_None)]
    每步一个描述 + SQL 语句 (或可调用)
    """
    plan = []

    # ── Step 1: CREATE TABLE projects ──────────────────────────────────
    plan.append((
        "1/7 创建 projects 表",
        """
        CREATE TABLE IF NOT EXISTS projects (
            project_id          TEXT PRIMARY KEY,
            project_name        TEXT NOT NULL,
            customer_name       TEXT,
            project_type        TEXT,
            project_status      TEXT DEFAULT 'active',

            total_contract_amount REAL DEFAULT 0,

            planned_start       TEXT,
            planned_end         TEXT,
            actual_start        TEXT,
            actual_end          TEXT,

            project_manager     TEXT,
            tech_lead           TEXT,
            sales_lead          TEXT,

            overall_progress    REAL DEFAULT 0,
            risk_level          TEXT DEFAULT 'low',

            created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        None,
    ))

    # ── Step 2: CREATE TABLE contract_project_link ───────────────────
    plan.append((
        "2/7 创建 contract_project_link 表",
        """
        CREATE TABLE IF NOT EXISTS contract_project_link (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id     TEXT NOT NULL,
            project_id      TEXT NOT NULL,
            link_type       TEXT DEFAULT 'primary',
            link_note       TEXT,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        )
        """,
        None,
    ))

    # ── Step 3: CREATE TABLE contract_files ──────────────────────────
    plan.append((
        "3/7 创建 contract_files 表",
        """
        CREATE TABLE IF NOT EXISTS contract_files (
            file_id         TEXT PRIMARY KEY,
            contract_id     TEXT NOT NULL,
            file_name       TEXT NOT NULL,
            file_type       TEXT NOT NULL,
            file_path       TEXT,
            file_size       INTEGER,
            upload_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            upload_by       TEXT,
            is_latest       BOOLEAN DEFAULT 1,
            version         TEXT DEFAULT 'v1',
            notes           TEXT,
            FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
        )
        """,
        None,
    ))

    # ── Step 4: CREATE TABLE personnel ───────────────────────────────
    plan.append((
        "4/7 创建 personnel 表",
        """
        CREATE TABLE IF NOT EXISTS personnel (
            person_id       TEXT PRIMARY KEY,
            person_name     TEXT NOT NULL,
            phone           TEXT,
            email           TEXT,
            department      TEXT,
            role_tags       TEXT,
            status          TEXT DEFAULT 'active',
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        None,
    ))

    # ── Step 5: CREATE TABLE project_personnel ───────────────────────
    plan.append((
        "5/7 创建 project_personnel 表",
        """
        CREATE TABLE IF NOT EXISTS project_personnel (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id      TEXT NOT NULL,
            person_id       TEXT NOT NULL,
            role_type       TEXT NOT NULL,
            assigned_date   TEXT,
            is_active       BOOLEAN DEFAULT 1,
            FOREIGN KEY (project_id) REFERENCES projects(project_id),
            FOREIGN KEY (person_id) REFERENCES personnel(person_id)
        )
        """,
        None,
    ))

    # ── Step 6: CREATE TABLE payment_vouchers ────────────────────────
    plan.append((
        "6/7 创建 payment_vouchers 表",
        """
        CREATE TABLE IF NOT EXISTS payment_vouchers (
            voucher_id          TEXT PRIMARY KEY,
            supplier_contract_id INTEGER NOT NULL,
            supplier_id         TEXT NOT NULL,
            project_id          TEXT,
            voucher_date        TEXT,
            amount              REAL NOT NULL,
            voucher_no          TEXT,
            payment_method      TEXT,
            attachment_path     TEXT,
            notes               TEXT,
            created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by          TEXT,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        )
        """,
        None,
    ))

    # ── Step 7: migration callback (动态 SQL 和数据操作) ────────────
    plan.append((
        "7/7 contracts 扩展 + 项目初始化 + 回填 project_id",
        None,  # 无静态 SQL，由 callback 处理
        "_run_migration_steps",
    ))

    return plan


def _run_migration_steps(conn: sqlite3.Connection, cur: sqlite3.Cursor, dry_run: bool):
    """执行所有动态迁移步骤 (ALTER TABLE + 数据操作)"""

    # ─── 7a. contracts 新增列 ──────────────────────────────────────────
    log("7a. 扩展 contracts 表 (7 个新字段)...", dry_run)
    contracts_new_cols = [
        ("official_name", "TEXT"),
        ("sgsc_id", "TEXT"),
        ("ocr_doc_path", "TEXT"),
        ("contract_status", "TEXT DEFAULT 'signed'"),
        ("estimated_amount", "REAL"),
        ("tax_inclusive", "BOOLEAN DEFAULT 0"),
        ("change_history", "TEXT"),
    ]
    for col_name, col_type in contracts_new_cols:
        if not column_exists(cur, "contracts", col_name):
            sql = f"ALTER TABLE contracts ADD COLUMN {col_name} {col_type}"
            log(f"  -> contracts ADD {col_name} {col_type}", dry_run)
            if not dry_run:
                cur.execute(sql)
        else:
            log(f"  -> contracts.{col_name} 已存在，跳过", dry_run)

    # ─── 7b. stages / payments / deliverables 加 project_id ──────────
    for tbl in ("stages", "payments", "deliverables"):
        log(f"7b. 扩展 {tbl} 表 (project_id)...", dry_run)
        if not column_exists(cur, tbl, "project_id"):
            sql = f"ALTER TABLE {tbl} ADD COLUMN project_id TEXT"
            log(f"  -> {tbl} ADD project_id TEXT", dry_run)
            if not dry_run:
                cur.execute(sql)
        else:
            log(f"  -> {tbl}.project_id 已存在，跳过", dry_run)

    # ─── 7c. payments 再加 paid_amount / paid_date ──────────────────
    log("7c. 扩展 payments 表 (paid_amount, paid_date)...", dry_run)
    payments_new_cols = [
        ("paid_amount", "REAL DEFAULT 0"),
        ("paid_date", "TEXT"),
    ]
    for col_name, col_type in payments_new_cols:
        if not column_exists(cur, "payments", col_name):
            sql = f"ALTER TABLE payments ADD COLUMN {col_name} {col_type}"
            log(f"  -> payments ADD {col_name} {col_type}", dry_run)
            if not dry_run:
                cur.execute(sql)
        else:
            log(f"  -> payments.{col_name} 已存在，跳过", dry_run)

    # ─── 7d. 初始化 50 个项目 (1:1 复用 contract_id) ─────────────────
    log("7d. 初始化 projects (从 contracts 复制数据)...", dry_run)
    # 读取所有合同
    cur.execute("""
        SELECT contract_id, project_name, project_type,
               party_a, contract_amount, sign_date, expiry_date,
               project_leader, created_at
        FROM contracts
        ORDER BY contract_id
    """)
    all_contracts = cur.fetchall()
    log(f"  读取到 {len(all_contracts)} 个合同记录", dry_run)

    # 查一下 projects 表当前有多少条 (增量幂等)
    existing_projects = 0
    try:
        cur.execute("SELECT COUNT(*) FROM projects")
        existing_projects = cur.fetchone()[0]
    except sqlite3.OperationalError:
        pass  # 表还不存在（dry-run 正常）
    log(f"  projects 表现有 {existing_projects} 条", dry_run)

    insert_count = 0
    for row in all_contracts:
        (
            cid, pname, ptype, party_a, amount,
            sign_date, expiry_date, leader, created_at,
        ) = row

        # skip already-initialized (dry-run 下不检查—表不一定存在)
        if not dry_run:
            cur.execute("SELECT 1 FROM projects WHERE project_id = ?", (cid,))
            if cur.fetchone():
                continue

        insert_count += 1
        if dry_run:
            log(f"  [INSERT] project_id={cid}, name={pname}", dry_run)
        else:
            cur.execute(
                """
                INSERT INTO projects (
                    project_id, project_name, customer_name, project_type,
                    project_status, total_contract_amount,
                    planned_start, planned_end,
                    project_manager
                ) VALUES (?, ?, ?, ?, 'active', ?, ?, ?, ?)
                """,
                (
                    cid,
                    pname,
                    party_a,
                    ptype or "未知",
                    amount or 0,
                    sign_date or "",
                    expiry_date or "",
                    leader or "",
                ),
            )

    log(f"  新插入 {insert_count} 条 project 记录", dry_run)

    # ─── 7e. 初始化 contract_project_link (1:1) ──────────────────────
    log("7e. 初始化 contract_project_link (1:1)...", dry_run)
    cur.execute("SELECT contract_id FROM contracts ORDER BY contract_id")
    contract_ids = [r[0] for r in cur.fetchall()]

    existing_links = 0
    try:
        cur.execute("SELECT COUNT(*) FROM contract_project_link")
        existing_links = cur.fetchone()[0]
    except sqlite3.OperationalError:
        pass  # 表还不存在（dry-run 正常）
    log(f"  contract_project_link 现有 {existing_links} 条", dry_run)

    link_count = 0
    for cid in contract_ids:
        if not dry_run:
            cur.execute(
                "SELECT 1 FROM contract_project_link WHERE contract_id = ? AND project_id = ?",
                (cid, cid),
            )
            if cur.fetchone():
                continue
        link_count += 1
        if dry_run:
            log(f"  [INSERT] contract_id={cid} -> project_id={cid}", dry_run)
        else:
            cur.execute(
                """
                INSERT INTO contract_project_link (contract_id, project_id, link_type)
                VALUES (?, ?, 'primary')
                """,
                (cid, cid),
            )

    log(f"  新插入 {link_count} 条 contract_project_link 记录", dry_run)

    # ─── 7f. 回填 stages / payments / deliverables 的 project_id ───
    for tbl in ("stages", "payments", "deliverables"):
        log(f"7f. 回填 {tbl}.project_id...", dry_run)
        if column_exists(cur, tbl, "project_id"):
            cur.execute(
                f"UPDATE {tbl} SET project_id = contract_id "
                f"WHERE project_id IS NULL AND contract_id IS NOT NULL"
            )
            affected = cur.rowcount if not dry_run else 0
            log(f"  -> {tbl} 更新 {affected} 条记录", dry_run)
        else:
            log(f"  -> {tbl} 无 project_id 列，跳过", dry_run)

    # ─── 7g. 验证 ──────────────────────────────────────────────────────
    log("7g. 验证迁移结果...", dry_run)
    if dry_run:
        log("  (跳过计数验证)", dry_run)
    else:
        cur.execute("SELECT COUNT(*) FROM projects")
        p_cnt = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM contract_project_link")
        l_cnt = cur.fetchone()[0]

        for tbl in ("stages", "payments", "deliverables"):
            cur.execute(
                f"SELECT COUNT(*) FROM {tbl} WHERE project_id IS NOT NULL"
            )
            filled = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {tbl}")
            total = cur.fetchone()[0]
            log(f"  {tbl}: project_id 已填 {filled}/{total}")

        log(f"  projects 总数: {p_cnt}")
        log(f"  contract_project_link 总数: {l_cnt}")


# ═══════════════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    dry_run = "--dry-run" in sys.argv

    print("=" * 60)
    print(f"PM-Director v3.0 数据库迁移")
    print(f"数据库: {DB_PATH}")
    print(f"模式:   {'DRY-RUN (仅预览)' if dry_run else '实际执行'}")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"[ERROR] 数据库文件不存在: {DB_PATH}")
        sys.exit(1)

    plan = build_sql_plan()

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()

    try:
        if not dry_run:
            cur.execute("BEGIN")
            log(">>> 事务开始")

        # 执行静态 DDL
        for label, sql, callback_ref in plan:
            if sql is not None:
                log(f"\n>>> {label}")
                s = sql.strip()
                if s:
                    log(f"  SQL: {s[:80]}...", dry_run)
                    if not dry_run:
                        cur.execute(s)
            elif callback_ref == "_run_migration_steps":
                log(f"\n>>> {label}")
                _run_migration_steps(conn, cur, dry_run)

        if dry_run:
            print("\n" + "=" * 60)
            print("DRY-RUN 完成 — 以上 SQL 均未执行")
            print("=" * 60)
        else:
            conn.commit()
            print("\n" + "=" * 60)
            print("迁移成功完成 [OK]")
            print("=" * 60)
            log(">>> 事务已提交")

    except Exception as e:
        if not dry_run:
            conn.rollback()
            print(f"\n[ERROR] 迁移失败，事务已回滚: {e}")
        else:
            print(f"\n[ERROR] 语法检查失败: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
