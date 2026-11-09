
from PyQt6.QtWidgets import QSystemTrayIcon, QApplication, QMenu
from PyQt6.QtGui import QIcon, QAction
from utils.paths import resource_path


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(QIcon(resource_path("icon/app.png")), parent)
        self.setToolTip("Мои задачки")

        tray_menu = QMenu(parent)

        show_action = QAction("Показать", self)
        show_action.triggered.connect(self.show_parent)
        tray_menu.addAction(show_action)

        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)

        self.setContextMenu(tray_menu)
        self.activated.connect(self.on_tray_activated)
        self.show()

    def show_parent(self):
        parent = self.parent()
        if parent is not None:
            parent.showNormal()
            parent.activateWindow()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_parent()