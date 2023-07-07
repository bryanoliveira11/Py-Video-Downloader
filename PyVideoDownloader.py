import sys

from PySide6.QtWidgets import QApplication

from Scripts import MainWindowClass

if __name__ == '__main__':
    qt = QApplication(sys.argv)
    App_main = MainWindowClass.PythonDownloader()
    App_main.show()
    qt.exec()
