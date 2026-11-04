from dataclasses import dataclass
import sys, os, json
from typing import List
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QLabel, QListWidgetItem,
    QMessageBox, QStyle, QMainWindow
)

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QKeySequence, QShortcut, QAction

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def data_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), filename)
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

DATA_FILE = data_path("tasks.json")
QSS_PATH = resource_path("style.qss")

def load_stylesheet():
    try:
        with open(QSS_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except OSError:
        return ""

@dataclass
class Task:
    text: str
    done: bool = False

class TaskModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks: List[Task] = []

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
            return Qt.CheckState.Checked if task.done else Qt.CheckState.Unchecked
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
        )

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid() or not (0 <= index.row() < len(self._tasks)):
            return False
        if role == Qt.ItemDataRole.CheckStateRole:
            self._tasks[index.row()].done = bool(value)
            self.dataChanged.emit(
                index, index,
                [Qt.ItemDataRole.CheckStateRole, Qt.ItemDataRole.FontRole],
            )
            return True
        return False

    def add_task(self, text: str) -> None:
        row = len(self._tasks)
        self.beginInsertRows(QModelIndex(), row, row)
        self._tasks.append(Task(text))
        self.endInsertRows()

    def remove_task(self, row: int) -> None:
        if 0 <= row < len(self._tasks):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._tasks[row]
            self.endRemoveRows()

    def clear(self) -> None:
        if not self._tasks:
            return
        self.beginResetModel()
        self._tasks.clear()
        self.endResetModel()

    def load(self, tasks: List[Task]) -> None:
        self.beginResetModel()
        self._tasks = tasks
        self.endResetModel()

    def tasks(self) -> List[Task]:
        return self._tasks


class TodoWidget(QWidget):

    countchanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Что нужно сделать?")

        self.add_button = QPushButton("Добавить")
        self.delete_button = QPushButton("Удалить")
        self.clear_all_button = QPushButton("Очистить всё")

        self.task_list = QListWidget()
        self.counter = QLabel()

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.add_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.counter)
        main_layout.addWidget(self.task_list)
        self.setLayout(main_layout)

        self.add_button.clicked.connect(self.add_task)
        self.input_field.returnPressed.connect(self.add_task)
        self.delete_button.clicked.connect(self.delete_task)
        self.clear_all_button.clicked.connect(self.clear_all_tasks)
        self.task_list.itemChanged.connect(self.on_changed_item)

        self.load_task()
        self.update_counter()

    def add_task(self):
        text = self.input_field.text().strip()
        if not text:
            return
        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Unchecked)
        self.task_list.addItem(item)

        self.input_field.clear()
        self.input_field.setFocus()
        self.update_counter()

    def delete_task(self):
        row = self.task_list.currentRow()
        if row >= 0:
            self.task_list.takeItem(row)
        self.update_counter()

    def clear_all_tasks(self):
        self.task_list.clear()
        self.update_counter()

    def on_changed_item(self, item):
        font = item.font()
        font.setStrikeOut(item.checkState() == Qt.CheckState.Checked)
        item.setFont(font)

    def update_counter(self):
        count = self.task_list.count()
        self.counter.setText(f"Всего задач: {count}")
        self.countchanged.emit(count)

    def load_task(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return
        for task in data:
            item = QListWidgetItem(task['text'])
            item.setFlags(item.flags() 
            | Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsEditable
            )
            self.task_list.addItem(item)
            if task.get("done", False):
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)

    def save_tasks(self):
        data = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            data.append({
                "text": item.text(),
                "done": item.checkState() == Qt.CheckState.Checked,
            })
        try:
            with open(DATA_FILE, 'w', encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"Не удалось сохранить задачи:{e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мои задачки")
        self.resize(340,700)
        self.setWindowIcon(QIcon(resource_path("icon/app.png")))

        self.todo = TodoWidget()
        self.setCentralWidget(self.todo)

        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        self.create_statusbar()

        self.todo.countchanged.connect(self.on_count_changed)

    def create_actions(self):
        self.save_action = QAction("&Сохранить", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setStatusTip("Сохранить задачи в файл")
        self.save_action.triggered.connect(self.todo.save_tasks)

        self.exit_action = QAction("&Выход", self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.setStatusTip("Закрыть приложение")
        self.exit_action.triggered.connect(self.close)

        self.add_action = QAction("&Добавить задачу", self)
        self.add_action.setShortcut(QKeySequence("Ctrl+N"))
        self.add_action.setStatusTip("Перейти к полю ввода")
        self.add_action.triggered.connect(self.todo.input_field.setFocus)

        self.delete_action = QAction("&Удалить задачу", self)
        self.delete_action.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        self.delete_action.setStatusTip("Удалить выбранную задачу")
        self.delete_action.triggered.connect(self.todo.delete_task)
        self.delete_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.todo.task_list.addAction(self.delete_action)

        self.clear_action = QAction("&Очистить всё", self)
        self.clear_action.setStatusTip("Удалить все задачи")
        self.clear_action.triggered.connect(self.on_clear_clicked)

        self.about_action = QAction("&О программе", self)
        self.about_action.setStatusTip("Информация о приложении")
        self.about_action.triggered.connect(self.show_about)

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Файл")
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        task_menu = menubar.addMenu("&Задачи")
        task_menu.addAction(self.add_action)
        task_menu.addAction(self.delete_action)
        task_menu.addSeparator()
        task_menu.addAction(self.clear_action)

        help_menu = menubar.addMenu("&Справка")
        help_menu.addAction(self.about_action)

    def create_toolbar(self):
        toolbar = self.addToolBar("Инструменты")
        toolbar.setMovable(False)

        style = self.style()
        self.save_action.setIcon(QIcon(resource_path("icon/save.png")))
        self.add_action.setIcon(QIcon(resource_path("icon/add.png")))
        self.delete_action.setIcon(QIcon(resource_path("icon/remove.png")))
        self.clear_action.setIcon(QIcon(resource_path("icon/clear.png")))

        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.add_action)
        toolbar.addAction(self.delete_action)
        toolbar.addSeparator()
        toolbar.addAction(self.clear_action)

    def create_statusbar(self):
        self.statusBar().showMessage("Готово")

    def on_count_changed(self, count):
        self.statusBar().showMessage(f"Задач: {count}")

    def on_clear_clicked(self):
        if self.todo.task_list.count() == 0:
            return
        answer = QMessageBox.question(
            self, "Очистить всё", "Удалить все задачи? Это действие нельзя отменить", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.todo.clear_all_tasks()

    def show_about(self):
        QMessageBox.about(
            self, "О программе",
            "<h2>Мои задачи</h2>"
            "<p>Простой менеджер задач на PyQt6</p>"
            "<p>Учебный проект ZerHI_TI</p>"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    app.setWindowIcon(QIcon(resource_path("icon/app-icon.png")))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())