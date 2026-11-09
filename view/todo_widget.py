from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListView, QLabel,
    QMessageBox, QAbstractItemView,
)
from PyQt6.QtCore import Qt, pyqtSignal


from model import storage
from model.task_model import TaskModel


class TodoWidget(QWidget):
    countchanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.model = TaskModel(self)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Что нужно сделать?")

        self.add_button = QPushButton("Добавить")
        self.delete_button = QPushButton("Удалить")
        self.clear_all_button = QPushButton("Очистить всё")

        self.task_list = QListView()
        self.task_list.setModel(self.model)
        self.task_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.task_list.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
        )

        self.counter = QLabel()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Поиск...")

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.add_button)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.clear_all_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.search_field)
        main_layout.addWidget(self.counter)
        main_layout.addWidget(self.task_list)
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

        self.add_button.clicked.connect(self.add_task)
        self.input_field.returnPressed.connect(self.add_task)
        self.delete_button.clicked.connect(self.delete_task)
        self.clear_all_button.clicked.connect(self.clear_all_tasks)
        self.search_field.textChanged.connect(self.refresh)

        self.model.rowsInserted.connect(lambda *_: self.refresh())
        self.model.rowsRemoved.connect(lambda *_: self.refresh())
        self.model.modelReset.connect(lambda *_: self.refresh())
        self.model.dataChanged.connect(lambda *_: self.refresh())

        self.load_task()
        self.update_counter()

    def add_task(self):
        text = self.input_field.text().strip()
        if not text:
            return
        self.model.add_task(text)
        self.input_field.clear()
        self.input_field.setFocus()

    def delete_task(self):
        index = self.task_list.currentIndex()
        if index.isValid():
            self.model.remove_task(index.row())

    def clear_all_tasks(self):
        if self.model.rowCount() == 0:
            return
        answer = QMessageBox.question(
            self, "Очистить всё",
            "Удалить все задачи? Это действие нельзя отменить",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.model.clear()

    def filter_tasks(self):
        text = self.search_field.text().lower().strip()
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 0)
            task_text = self.model.data(index, Qt.ItemDataRole.DisplayRole) or ""
            self.task_list.setRowHidden(row, text not in task_text.lower())

    def update_counter(self):
        total = self.model.rowCount()
        visible = sum(
            1 for row in range(total) 
            if not self.task_list.isRowHidden(row)
        )
        if total == visible:
            self.counter.setText(f"Всего задач: {total}")
        else:
            self.counter.setText(f"Всего задач: {total}, показано: {visible}")
        self.countchanged.emit(total)

    def refresh(self):
        self.filter_tasks()
        self.update_counter()

    def load_task(self):
        tasks = storage.load_task()
        if tasks:
            self.model.load(tasks)

    def save_tasks(self):
        try:
            storage.save_tasks(self.model.tasks())
        except OSError as e:
            QMessageBox.warning(
                self, "Ошибка", f"Не удалось сохранить задачи: {e}"
            )