from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
import sys

def main():
    app = QApplication(sys.argv)

    with open("tierpass_dark.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()