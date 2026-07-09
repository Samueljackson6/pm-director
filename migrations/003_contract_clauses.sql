-- 003_contract_clauses.sql
-- #3.② DB 结构优化：新增合同违约/罚款条款表 + 税率字段
-- 应用于 database/project_management.db（SQLite）

-- 1) contracts 表新增税率数值字段（原仅有 tax_inclusive bool）
ALTER TABLE contracts ADD COLUMN tax_rate REAL DEFAULT NULL;

-- 2) 新增合同条欒表（条款级，一行一条款）
CREATE TABLE IF NOT EXISTS contract_clauses (
  clause_id       TEXT PRIMARY KEY,
  contract_id     TEXT NOT NULL,
  clause_category TEXT NOT NULL,   -- breach_liability|liquidated_damages|penalty|overdue|compensation|confidentiality|ip|force_majeure|termination
  trigger_type    TEXT,            -- 逾期交付|验收不通过|保密违约|解除合同|其他
  rate_pct        REAL,            -- 违约金/罚款比例（占报酬 %）
  ld_base         TEXT DEFAULT '技术服务报酬',
  threshold_days  INTEGER,         -- 逾期解除阈值（N 日）
  refund_full     BOOLEAN DEFAULT 0,-- 是否退还全部款项
  clause_text     TEXT,            -- 原文片段（留痕）
  source_doc      TEXT,            -- 源 DOCX 文件名
  extracted_at    TEXT,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);
CREATE INDEX IF NOT EXISTS idx_cc_contract ON contract_clauses(contract_id);
CREATE INDEX IF NOT EXISTS idx_cc_cat ON contract_clauses(clause_category);
