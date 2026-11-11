"""SQLite 数据库连接与表结构初始化。"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "students.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    student_no TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    gender     TEXT DEFAULT '',
    major      TEXT DEFAULT '',
    grade      INTEGER DEFAULT 0,
    chinese    REAL DEFAULT 0,
    math       REAL DEFAULT 0,
    english    REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection(db_path=None):
    """获取数据库连接，行结果按字典方式访问。"""
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn):
    """初始化表结构（幂等，可重复调用）。"""
    conn.executescript(SCHEMA)
    conn.commit()
