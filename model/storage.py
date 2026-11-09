import json
import os
from typing import List

from .task import Task
from utils.paths import DATA_FILE


def load_task() -> List[Task]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    return [
        Task(text=entry.get("text", ""), done=bool(entry.get("done", False)))
        for entry in data
        if entry.get("text")
    ]

def save_tasks(tasks: List[Task]) -> None:
    data = [{"text": t.text, "done": t.done} for t in tasks]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)