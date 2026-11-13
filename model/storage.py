import sqlite3
from contextlib import contextmanager
from typing import List, Optional

from .task import Task
from utils.paths import DB_FILE

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db() -> None:
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
            )        
        """)

def load_task() -> List[Task]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, text, done FROM tasks ORDER BY id"
        ).fetchall()
    return [Task(id=r["id"], text=r["text"], done=bool(r["done"])) for r in rows]

def insert_task(text: str) -> Task:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (text, done) VALUES (?, 0)", (text,)
        )
        return Task(id=cur.lastrowid, text=text, done=False)

def update_task_text(task_id: int, text: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE tasks SET text = ? WHERE id = ?", (text, task_id)
        )

def update_task_done(task_id: int, done: bool) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE tasks SET done = ? WHERE id = ?", (int(done), task_id)
        )

def delete_task(task_id: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM tasks WHERE id = ?", (task_id,)
        )

def clear_tasks() -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM tasks")