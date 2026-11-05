from PyQt6.QtWidgets import (
    QMessageBox, QMainWindow
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QKeySequence, QAction
from utils.paths import resource_path
from .todo_widget import TodoWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мои задачки")
        self.resize(340, 700)
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
        self.add_action.triggered.connect(lambda: self.todo.input_field.setFocus())

        self.delete_action = QAction("&Удалить задачу", self)
        self.delete_action.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        self.delete_action.setStatusTip("Удалить выбранную задачу")
        self.delete_action.triggered.connect(self.todo.delete_task)
        self.delete_action.setShortcutContext(Qt.ShortcutContext.WidgetShortcut)
        self.todo.task_list.addAction(self.delete_action)

        self.clear_action = QAction("&Очистить всё", self)
        self.clear_action.setStatusTip("Удалить все задачи")
        self.clear_action.triggered.connect(self.todo.clear_all_tasks)

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

    def show_about(self):
        QMessageBox.about(
            self, "О программе",
            "<h2>Мои задачи</h2>"
            "<p>Простой менеджер задач на PyQt6</p>"
            "<p>Учебный проект ZerHI_TI</p>",
        )

    def closeEvent(self, event):
        self.todo.save_tasks()
        super().closeEvent(event)
