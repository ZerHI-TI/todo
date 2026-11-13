from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    text: str
    done: bool = False
    id: Optional[int] = None