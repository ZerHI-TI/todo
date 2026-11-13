import os
import sys


def resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def data_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), filename)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename)

DATA_FILE = data_path("tasks.json")
DB_FILE = data_path("tasks.db")
QSS_PATH = resource_path("style.qss")

def load_stylesheet():
    try:
        with open(QSS_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except OSError:
        return ""