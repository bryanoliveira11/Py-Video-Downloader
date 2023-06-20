from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie, QPixmap
from PySide6.QtWidgets import QFileDialog, QMainWindow

from designs.design_Options import Ui_DownloaderOptions

from . import MainWindowClass, threads
from .DownloadClass import DownloadWindow


class OptionsWindow(Ui_DownloaderOptions, QMainWindow):
    def __init__(self, MainWindow, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.MainWindowAttributes: MainWindowClass.PythonDownloader = MainWindow
        self.setFixedSize(800, 600)
        self.DownloadWindow = None

        self.app_title.setText("DOWNLOAD OPTIONS")
        self.Play_Text.setText("PLAYLIST OPTIONS")
        self.Res_text.setText("RESOLUTION")
        self.D_Full.setText("Download Full Playlist")
        self.D_Interval.setText("Download a Interval")
        self.D_Path_Text.setText("DOWNLOAD PATH")
        self.End_Num.setPlaceholderText("end num")
        self.Start_Num.setPlaceholderText("start num")

        # set gif to the options screen
        loading_gif = QMovie(".\\designs\\bkp_ui\\../../imgs/options_gif.gif")
        self.optionsIcon.setMovie(loading_gif)
        loading_gif.start()

        # resolutions and playlist lists / function to validate all
        self.Resolutions_List = [
            self.Res_1080p, self.Res_720p, self.Res_480p, self.Res_360p
        ]
        self.Playlist_OptionsList = [self.D_Full, self.D_Interval]
        self.Playlist_InputsList = [self.End_Num, self.Start_Num]

        # get the methods to work on that class
        self.getvideoTitleThumbnail()
        self.Checkboxes_Validation()
        self.DisablePlaylistWhenVideo()
        self.getDownloadPathFromTxt()
        self.btnBackMain.clicked.connect(self.BacktoMainWindow)
        self.btnSearchFolder.clicked.connect(self.SelectDownload_Path)
        self.btnDownload.clicked.connect(self.StartDownloadValidations)

    # function to get back to the first window when button is clicked.
    def BacktoMainWindow(self):
        self.hide()
        self.MainWindow = MainWindowClass.PythonDownloader()
        self.MainWindow.show()
        self.MainWindow.Url_Input.setText(
            self.MainWindowAttributes.Url_Input.text())
        self.MainWindow.SearchVideoURL()

    # this functions will get the thumb and title from the main window
    def getvideoTitleThumbnail(self):
        self.video_thumb_opt.setPixmap(
            QPixmap(self.MainWindowAttributes.Thumb_Image).scaledToWidth(360)
        )
        self.video_thumb_opt.setAlignment(Qt.AlignCenter)

        if not self.MainWindowAttributes.Type_of_URL == 'PLAYLIST':
            self.video_title_opt.setText(self.MainWindowAttributes.Video_Title)
        else:
            self.video_title_opt.setText(
                f'{self.MainWindowAttributes.Video_Title} - ( {self.MainWindowAttributes.Quantity_of_Videos} VIDEOS )')

        self.video_title_opt.setAlignment(Qt.AlignCenter)

    # will disable the checkboxes when the download is a single video
    def DisablePlaylistWhenVideo(self):
        if self.MainWindowAttributes.Type_of_URL == 'VIDEO':
            for option_boxes in self.Playlist_OptionsList:
                option_boxes.setEnabled(False)

            for option_inputs in self.Playlist_InputsList:
                option_inputs.setEnabled(False)

    # set a connect state changed event to validate what checkbox
    # is checked by user at options screen
    def Checkboxes_Validation(self):

        # default None to the variables for later validations
        self.Resolution_Download = self.Playlist_Download = None

        # get all checkboxes from Resolutions_List and set the function
        for Resolutions in self.Resolutions_List:
            Resolutions.clicked.connect(self.ValidateResolution_CheckBoxes)

        # get all checkboxes from Playlist_OptionsList and set the function
        for PlaylistOption in self.Playlist_OptionsList:
            PlaylistOption.clicked.connect(self.ValidatePlaylist_CheckBoxes)

    # change the checked boxes by sender validation ; Resolutions
    def ValidateResolution_CheckBoxes(self):
        try:
            for Res in range(len(self.Resolutions_List)):
                self.currentResCheckbox = self.Resolutions_List[Res]

                if self.currentResCheckbox.isChecked() and self.currentResCheckbox != self.sender():
                    self.currentResCheckbox.setChecked(False)

                SelectedRes = {
                    self.Res_1080p.isChecked(): '1080p',
                    self.Res_720p.isChecked(): '720p',
                    self.Res_480p.isChecked(): '480p',
                    self.Res_360p.isChecked(): '360p',
                }

            self.Resolution_Download = SelectedRes[True]

        except KeyError:
            self.Resolution_Download = None

    # change the checked boxes by Qt.Checked sender validation
    # ; Playlist Options
    def ValidatePlaylist_CheckBoxes(self):
        try:

            for PlaylistOptions in range(len(self.Playlist_OptionsList)):

                self.currentPlaylistCheckbox = self.Playlist_OptionsList[PlaylistOptions]

                if self.currentPlaylistCheckbox.isChecked() and self.currentPlaylistCheckbox != self.sender():
                    self.currentPlaylistCheckbox.setChecked(False)

                SelectedPlaylistOption = {
                    self.D_Full.isChecked(): 'Full Playlist',
                    self.D_Interval.isChecked(): 'Interval Videos',
                }

                self.Playlist_Download = SelectedPlaylistOption[True]

                if self.D_Full.isChecked():
                    self.Start_Num.setText('')
                    self.End_Num.setText('')
                    self.Start_Num.setEnabled(False)
                    self.End_Num.setEnabled(False)

                elif self.D_Interval.isChecked():
                    self.Start_Num.setEnabled(True)
                    self.End_Num.setEnabled(True)

        except KeyError:
            self.Playlist_Download = None

    def OpenDownloadWindow(self):  # opens the download window
        if self.DownloadWindow is None:
            self.DownloadWindow = DownloadWindow(self)
        self.hide()
        self.DownloadWindow.show()

    # functions to select a folder for downloads and create a txt to save it
    def SelectDownload_Path(self):

        self.Download_Folder = QFileDialog.getExistingDirectory()
        self.path_show.setEnabled(True)
        self.path_show.setText(self.Download_Folder)
        self.Download_Exception.setText('')

        # will create a txt file and save the folder inside
        with open('DownloadPath.txt', 'w') as DownloadPath:
            if not self.Download_Folder:
                self.path_show.setText(
                    '[INFO] : Your Download Path is Empty ! '
                )
                return

            DownloadPath.write(self.Download_Folder)

    # that function will open the txt DownloadPath and get the path
    def getDownloadPathFromTxt(self):
        try:
            # get last saved path from DownloadPath.txt and show at the screen
            with open('DownloadPath.txt') as readPath:
                self.path_show.setText(readPath.read())
        except FileNotFoundError:
            self.Download_Exception.setText(
                '[INFO] : Choose a Path to Download Before Start Downloading !')

    def StartDownloadValidations(self):
        try:
            # try to read the path to download
            with open('DownloadPath.txt') as readPath:
                self.Path = readPath.read()
                if self.Path == '':
                    self.Download_Exception.setText(
                        '[INFO] : Choose a Path to Download Before Start Downloading !'
                    )
                    return

        except FileNotFoundError:
            self.Download_Exception.setText(
                '[INFO] : Choose a Path to Download First !'
            )
            return

        if self.MainWindowAttributes.Type_of_URL == 'PLAYLIST' and self.Playlist_Download is None or self.Resolution_Download is None:
            self.Download_Exception.setText(
                '[INFO] : Check all the Options to Download !'
            )
            return

        if not self.MainWindowAttributes.Type_of_URL == 'PLAYLIST' and self.Resolution_Download is not None:
            self.DownloadSingleVideo()

        if self.D_Full.isChecked() and self.Resolution_Download is not None:
            self.DownloadFullPlaylist()  # calls function to playlist download

        if self.D_Interval.isChecked() and self.Resolution_Download is not None:
            self.ValidateInputs_Interval()

    # function to start threads and connect updateUI
    def DownloadThread_Start(self, thread_name):
        thread_name.ShowVideoTitle.connect(
            self.DownloadWindow.UpdateUI_Title
        )
        thread_name.Update_Gif.connect(
            self.DownloadWindow.UpdateUI_GIFS
        )
        thread_name.Status_Text.connect(
            self.DownloadWindow.UpdateUI_Status
        )
        thread_name.Media_Home_Btns.connect(
            self.DownloadWindow.UpdateUI_ShowBtns
        )
        thread_name.start()

    # Function to download a single video, it calls the SV Thread and uses
    # the connect to update the UI with text and gif status
    def DownloadSingleVideo(self):
        self.OpenDownloadWindow()
        self.DownloadSV_Thread = threads.DownloadSingleVideo_Thread(
            self.MainWindowAttributes.Youtube_Video,
            self.Resolution_Download, self.Path
        )
        self.DownloadThread_Start(self.DownloadSV_Thread)

    # function to download full playlist calls a DownloadFP_Thread thread
    def DownloadFullPlaylist(self):
        self.OpenDownloadWindow()
        self.DownloadFP_Thread = threads.DownloadFP_Thread(
            self.MainWindowAttributes.Youtube_Video,
            self.Resolution_Download, self.Path,
            self.MainWindowAttributes.Quantity_of_Videos
        )
        self.DownloadThread_Start(self.DownloadFP_Thread)

    # function to download interval videos of a playlist
    def DownloadIntervalPlaylist(self):
        self.OpenDownloadWindow()
        self.DownloadIP_Thread = threads.DownloadIP_Thread(
            self.MainWindowAttributes.Youtube_Video,
            self.Resolution_Download, self.Path,
            self.MainWindowAttributes.Quantity_of_Videos,
            self.URL_Counter, self.List_Interval_URLS,
            self.Current_URL, self.StartInterval, self.EndInterval)
        self.DownloadThread_Start(self.DownloadIP_Thread)

    def ValidateInputs_Interval(self):
        try:
            # user start and end inputs
            self.StartInterval = int(self.Start_Num.text())
            self.EndInterval = int(self.End_Num.text())
            self.ListAll_URLS = (
                [0, *self.MainWindowAttributes.Youtube_Video.video_urls]
            )  # list of all urls in the playlist

            self.Current_URL = None  # it will save the current URL in the loop
            self.URL_Counter = 0  # counter starts at 0
            self.List_Interval_URLS = self.ListAll_URLS[
                self.StartInterval:self.EndInterval+1
            ]

            if self.StartInterval > self.EndInterval or self.StartInterval > self.MainWindowAttributes.Quantity_of_Videos or self.EndInterval > self.MainWindowAttributes.Quantity_of_Videos or self.StartInterval < 0 or self.EndInterval < 0 or self.StartInterval == 0 or self.EndInterval == 0:
                self.Download_Exception.setText(
                    f"[INFO] : Input Only Bigger Than 0 and in Range {self.MainWindowAttributes.Quantity_of_Videos} Numbers ! Start Must be < End "
                )
                self.Start_Num.setText('')
                self.End_Num.setText('')
            elif self.StartInterval == self.EndInterval:
                self.Download_Exception.setText(
                    "[INFO] : Your Start Can't be the Same as Your End "
                )
                self.End_Num.setText('')
            else:
                self.DownloadIntervalPlaylist()

        except ValueError:
            self.Download_Exception.setText("[INFO] : Input Only Numbers ! ")
            self.Start_Num.setText('')
            self.End_Num.setText('')
