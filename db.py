import sqlite3
from datetime import date
from typing import List, Dict, Any, Optional

DB_FILE = "habit_tracker.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    # สร้างตาราง habits
    conn.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            emoji TEXT DEFAULT '✨',
            interval_days INTEGER DEFAULT 1,
            start_date TEXT NOT NULL,
            weekdays TEXT DEFAULT ''
        )
    """)
    # เช็คว่ามีคอลัมน์ weekdays หรือยัง (เพื่อรองรับ DB เก่า)
    cursor = conn.execute("PRAGMA table_info(habits)")
    columns = [col["name"] for col in cursor.fetchall()]
    if "weekdays" not in columns:
        conn.execute("ALTER TABLE habits ADD COLUMN weekdays TEXT DEFAULT ''")

    # สร้างตาราง logs
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            log_date TEXT NOT NULL,
            note TEXT,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def add_habit(name: str, emoji: str, interval_days: int, start_date: date, weekdays: str = ""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO habits (name, emoji, interval_days, start_date, weekdays) VALUES (?, ?, ?, ?, ?)",
        (name, emoji, interval_days, start_date.isoformat(), weekdays)
    )
    conn.commit()
    conn.close()

def update_habit(habit_id: int, name: str, emoji: str, interval_days: int, start_date: date, weekdays: str = ""):
    conn = get_connection()
    conn.execute(
        "UPDATE habits SET name = ?, emoji = ?, interval_days = ?, start_date = ?, weekdays = ? WHERE id = ?",
        (name, emoji, interval_days, start_date.isoformat(), weekdays, habit_id),
    )
    conn.commit()
    conn.close()

def get_habits() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM habits ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_habit(habit_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.execute("DELETE FROM logs WHERE habit_id = ?", (habit_id,))
    conn.commit()
    conn.close()

def add_log(habit_id: Optional[int], log_date: date, note: Optional[str] = None, completed: bool = False):
    conn = get_connection()
    conn.execute(
        "INSERT INTO logs (habit_id, log_date, note, completed) VALUES (?, ?, ?, ?)",
        (habit_id, log_date.isoformat(), note, 1 if completed else 0)
    )
    conn.commit()
    conn.close()

def is_done_today(habit_id: int, check_date: date) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM logs WHERE habit_id = ? AND log_date = ? AND completed = 1",
        (habit_id, check_date.isoformat())
    ).fetchone()
    conn.close()
    return row is not None

def get_logs_for_date(check_date: date) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM logs WHERE log_date = ?", (check_date.isoformat(),)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_logs(limit: int = 500) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT l.*, h.name as habit_name, h.emoji as habit_emoji
        FROM logs l
        LEFT JOIN habits h ON l.habit_id = h.id
        ORDER BY l.log_date DESC, l.id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_log(log_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM logs WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()
