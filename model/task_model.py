from typing import List

from .task import Task
from . import storage
from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt
from PyQt6.QtGui import QFont

class TaskModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks: List[Task] = storage.load_task()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._tasks)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._tasks)):
            return None
        task = self._tasks[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return task.text
        if role == Qt.ItemDataRole.CheckStateRole:
            return Qt.CheckState.Checked.value if task.done else Qt.CheckState.Unchecked.value
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return task.text
        if role == Qt.ItemDataRole.FontRole:
            font = QFont()
            font.setStrikeOut(task.done)
            return font
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsEditable
        )

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid() or not (0 <= index.row() < len(self._tasks)):
            return False
        task = self._tasks[index.row()]

        if role == Qt.ItemDataRole.CheckStateRole:
            task.done = bool(value)
            storage.update_task_done(task.id, task.done)
            self.dataChanged.emit(
                index, index,
                [Qt.ItemDataRole.CheckStateRole],
            )
            return True

        if role == Qt.ItemDataRole.EditRole:
            text = str(value).strip()
            if not text or text == task.text:
                return False
            task.text = text
            storage.update_task_text(task.id, text)
            self.dataChanged.emit(
                index, index,
                [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole],
            )
            return True

        return super().setData(index, value, role)

    def add_task(self, text: str) -> None:
        text = text.strip()
        if not text:
            return
        task = storage.insert_task(text)
        row = len(self._tasks)
        self.beginInsertRows(QModelIndex(), row, row)
        self._tasks.append(task)
        self.endInsertRows()

    def remove_task(self, row: int) -> None:
        if 0 <= row < len(self._tasks):
            storage.delete_task(self._tasks[row].id)
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._tasks[row]
            self.endRemoveRows()

    def clear(self) -> None:
        if not self._tasks:
            return
        storage.clear_tasks()
        self.beginResetModel()
        self._tasks.clear()
        self.endResetModel()

    def load(self, tasks: List[Task]) -> None:
        self.beginResetModel()
        self._tasks = tasks
        self.endResetModel()

    def tasks(self) -> List[Task]:
        return self._tasks