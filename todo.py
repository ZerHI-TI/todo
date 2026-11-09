import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from utils.paths import load_stylesheet, resource_path
from view.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    app.setWindowIcon(QIcon(resource_path("icon/app.png")))
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()