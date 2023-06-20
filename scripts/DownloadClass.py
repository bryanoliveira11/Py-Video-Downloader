import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QMainWindow

from designs.design_Download import Ui_Download_Screen

from . import MainWindowClass


class DownloadWindow(Ui_Download_Screen, QMainWindow):
    def __init__(self, MainWindow, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.MainWindowAttributes = MainWindow
        self.MainWindow = MainWindowClass.PythonDownloader()
        self.setFixedSize(800, 575)
        self.UpdateStatusGif(".\\designs\\bkp_ui\\../../imgs/loading_gif.gif")
        self.btnMediaPlayer.hide()
        self.btnHome.hide()
        self.btnHome.clicked.connect(self.BacktoHome)  # return to main window
        self.btnMediaPlayer.clicked.connect(
            lambda: os.startfile(self.MainWindowAttributes.Path)
        )  # open the path file

    def UpdateStatusGif(self, gif_path):
        loading_gif = QMovie(gif_path)
        self.Status_gif.setMovie(loading_gif)
        loading_gif.start()

    def BacktoHome(self):
        self.hide()
        self.MainWindow.show()

    # function to update the ui with the signal from the Qthread
    def UpdateUI_Title(self, title):
        self.VideoTitle.setText(title)
        self.VideoTitle.setAlignment(Qt.AlignCenter)

    # function that updates the status message
    def UpdateUI_Status(self, color, status):
        self.StatusMessage.setText(status)
        self.StatusMessage.setAlignment(Qt.AlignCenter)
        self.StatusMessage.setStyleSheet(
            f"font: 75 11pt;Segoe UI;font-weight: 700;margin-left: 2px;color:{color}"
        )

    def UpdateUI_GIFS(self, gif_path):  # function that updates the status gif
        self.UpdateStatusGif(gif_path)

    # will emit a signal to show the btns after download
    def UpdateUI_ShowBtns(self):
        self.btnHome.show()
        self.btnMediaPlayer.show()
        self.txthome.setText('HOME')
        self.txtpath.setText('PATH')
