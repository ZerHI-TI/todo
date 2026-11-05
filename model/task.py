from dataclasses import dataclass


@dataclass
class Task:
    text: str
    done: bool = False