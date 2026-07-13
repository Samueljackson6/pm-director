"""发票文本编码修复工具测试。"""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.repair_invoice_text_encoding import repair_invoice_text_encoding


class RepairInvoiceTextEncodingTest(unittest.TestCase):
    """验证非法 GBK 字节可安全转换为 SQLite Unicode 文本。"""

    def test_dry_run_does_not_modify_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            self._create_db(db_path)

            result = repair_invoice_text_encoding(db_path, apply=False)

            self.assertEqual(result["affected_rows"], 1)
            raw = self._read_raw_status(db_path)
            self.assertEqual(raw, "已回款".encode("gbk"))

    def test_apply_converts_invalid_bytes_to_unicode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            self._create_db(db_path)

            result = repair_invoice_text_encoding(db_path, apply=True)

            self.assertEqual(result["affected_rows"], 1)
            con = sqlite3.connect(db_path)
            try:
                row = con.execute(
                    "SELECT invoice_type, status, payment_status, notes FROM invoices WHERE invoice_id=1"
                ).fetchone()
            finally:
                con.close()
            self.assertEqual(row, ("客户回款", "已回款", "已匹配", "验收后回款"))

    def test_apply_converts_utf8_blob_to_unicode_text(self):
        """即使字节本身可按 UTF-8 解码，也应从 BLOB 规范化为 TEXT。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            con = sqlite3.connect(db_path)
            try:
                con.execute(
                    "CREATE TABLE invoices (invoice_id INTEGER PRIMARY KEY, invoice_type TEXT, status TEXT, payment_status TEXT, notes TEXT)"
                )
                con.execute(
                    "INSERT INTO invoices VALUES (?, ?, ?, ?, ?)",
                    (1, b"receipt", b"paid", b"matched", b"note"),
                )
                con.commit()
            finally:
                con.close()

            result = repair_invoice_text_encoding(db_path, apply=True)

            self.assertEqual(result["affected_rows"], 1)
            con = sqlite3.connect(db_path)
            try:
                value_type = con.execute(
                    "SELECT typeof(status) FROM invoices WHERE invoice_id=1"
                ).fetchone()[0]
            finally:
                con.close()
            self.assertEqual(value_type, "text")

    def test_apply_leaves_normal_text_unchanged(self):
        """正常 SQLite TEXT 不应被误判为 BLOB。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            con = sqlite3.connect(db_path)
            try:
                con.execute(
                    "CREATE TABLE invoices (invoice_id INTEGER PRIMARY KEY, invoice_type TEXT, status TEXT, payment_status TEXT, notes TEXT)"
                )
                con.execute(
                    "INSERT INTO invoices VALUES (?, ?, ?, ?, ?)",
                    (1, "客户开票", "已开", "未匹配", "正常文本"),
                )
                con.commit()
            finally:
                con.close()

            result = repair_invoice_text_encoding(db_path, apply=True)

            self.assertEqual(result["affected_rows"], 0)

    @staticmethod
    def _create_db(db_path: Path) -> None:
        con = sqlite3.connect(db_path)
        try:
            con.execute(
                """
                CREATE TABLE invoices (
                    invoice_id INTEGER PRIMARY KEY,
                    invoice_type TEXT,
                    status TEXT,
                    payment_status TEXT,
                    notes TEXT
                )
                """
            )
            con.execute(
                "INSERT INTO invoices VALUES (?, ?, ?, ?, ?)",
                (
                    1,
                    "客户回款".encode("gbk"),
                    "已回款".encode("gbk"),
                    "已匹配".encode("gbk"),
                    "验收后回款".encode("gbk"),
                ),
            )
            con.commit()
        finally:
            con.close()

    @staticmethod
    def _read_raw_status(db_path: Path):
        con = sqlite3.connect(db_path)
        con.text_factory = bytes
        try:
            return con.execute("SELECT status FROM invoices WHERE invoice_id=1").fetchone()[0]
        finally:
            con.close()


if __name__ == "__main__":
    unittest.main()


