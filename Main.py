import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.showMaximized()
    app.exec()


if __name__ == '__main__':
    main()
