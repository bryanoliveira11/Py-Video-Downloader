import os
import re
import sys
from time import sleep

import requests
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QImage, QMovie, QPixmap
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow
from pytube import Playlist, YouTube

from designs.design_Download import Ui_Download_Screen
from designs.design_Main import Ui_PytubeDownloader
from designs.design_Options import Ui_DownloaderOptions


class PythonDownloader(QMainWindow, Ui_PytubeDownloader):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.setFixedSize(800, 600)
        self.OptionsWindow = None
        self.btnDownloadOptions.hide()
        self.Type_of_URL = ''
        self.Quantity_of_Videos = ''
        self.Video_URL = ''
        self.Video_Title = ''
        self.url_info.setText(
            "Copy and Paste the Youtube Video or Playlist Link Here :"
        )
        self.Thumb_Image = QImage()

        # search video function
        self.btnSearchVideo.clicked.connect(self.SearchVideoURL)
        # second window function
        self.btnDownloadOptions.clicked.connect(self.Open_Options_Window)

        # set python gif to the screen
        python_gif = QMovie(
            ".\\designs\\bkp_ui\\../../imgs/pythongif.gif"
        )
        self.python_ico.setMovie(python_gif)
        python_gif.start()

        # set github gif to the screen
        github_gif = QMovie(
            ".\\designs\\bkp_ui\\../../imgs/github_gif.gif"
        )
        self.githubgif.setMovie(github_gif)
        github_gif.start()

        self.txtgithub.setOpenExternalLinks(True)
        self.txtgithub.setText(
            "<a href='https://github.com/bryanoliveira11'>GitHub</a>"
        )

    # search video and validate re
    def SearchVideoURL(self):
        # re for videos
        self.VIDEO_RE = (
            r'^(http(s):\/\/.)[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$'
        )
        # re for playlist
        self.PLAYLIST_RE = (
            r'^https?:\/\/(www.youtube.com|youtube.com)\/playlist(.*)$'
        )

        # URL inputed by user
        self.Video_URL = str(self.Url_Input.text()).strip().replace(' ', '')
        self.Url_Input.setText('')

        try:
            if re.match(self.PLAYLIST_RE, self.Video_URL):
                self.Type_of_URL = 'PLAYLIST'

            elif re.match(self.VIDEO_RE, self.Video_URL):
                self.Type_of_URL = 'VIDEO'

            self.getUrl_Content()
            self.ScreenSearchDefaults()

        except Exception:
            self.Url_Exception.setText(
                '[ERROR] : Not Possible to Search the URL. Try Again ! <br/> \
                Make Sure that the Video/Playlist is not Private.'
            )
            self.Url_Exception.setAlignment(Qt.AlignCenter)
            self.HideVideoContent()

    # that function will get the videos title and thumbnail.
    # Also, will set Playlist for playlist and Youtube for video url
    def getUrl_Content(self):

        # setting title and thumbnail when video url
        if not self.Type_of_URL == 'PLAYLIST':
            self.Youtube_Video = YouTube(self.Video_URL)

            # get the thumbnail url
            Url_ThumbNail = self.Youtube_Video.thumbnail_url
            self.Quantity_of_Videos = 1
        else:
            self.Youtube_Video = Playlist(self.Video_URL)

            # this will get the first video thumbnail url
            Url_ThumbNail = YouTube(
                self.Youtube_Video.video_urls[0]
            ).thumbnail_url

            # get the amount of videos in the playlist
            self.Quantity_of_Videos = self.Youtube_Video.length

        # prevent user from using spaces in the url
        self.Video_Title = str(self.Youtube_Video.title).upper().strip()
        self.video_title.setText(f'{self.Video_Title}')  # setting the title

        # getting the thumbnail url and its content with requests
        self.Thumb_Image.loadFromData(requests.get(Url_ThumbNail).content)
        self.video_thumb.setPixmap(
            QPixmap(self.Thumb_Image).scaledToWidth(303)
        )
        self.video_thumb.setAlignment(Qt.AlignCenter)

    # that function will display the next button,
    # and display the type of url, quantity of videos
    def ScreenSearchDefaults(self):
        self.Url_Exception.setText('')
        self.btnDownloadOptions.show()
        self.video_type.setText(f'TYPE : {self.Type_of_URL}')
        self.video_qtd.setText(f'QUANTITY : {self.Quantity_of_Videos}')

    def HideVideoContent(self):  # hide things in main screen.
        self.video_title.setText('')
        self.video_type.setText('')
        self.video_qtd.setText('')
        self.video_thumb.setPixmap(QPixmap(''))
        self.btnDownloadOptions.hide()

    # open the options window and close the main
    def Open_Options_Window(self):
        if self.OptionsWindow is None:
            self.OptionsWindow = OptionsWindow(self)
        self.hide()
        self.OptionsWindow.show()


class OptionsWindow(Ui_DownloaderOptions, QMainWindow):
    def __init__(self, MainWindow, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.MainWindowAttributes = MainWindow
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
        self.MainWindow = PythonDownloader()
        self.MainWindow.show()

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
                if self.Path is None:
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
        self.DownloadSV_Thread = DownloadSingleVideo_Thread(
            self.MainWindowAttributes.Youtube_Video,
            self.Resolution_Download, self.Path
        )
        self.DownloadThread_Start(self.DownloadSV_Thread)

    # function to download full playlist calls a DownloadFP_Thread thread
    def DownloadFullPlaylist(self):
        self.OpenDownloadWindow()
        self.DownloadFP_Thread = DownloadFP_Thread(
            self.MainWindowAttributes.Youtube_Video,
            self.Resolution_Download, self.Path,
            self.MainWindowAttributes.Quantity_of_Videos
        )
        self.DownloadThread_Start(self.DownloadFP_Thread)

    # function to download interval videos of a playlist
    def DownloadIntervalPlaylist(self):
        self.OpenDownloadWindow()
        self.DownloadIP_Thread = DownloadIP_Thread(
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


class DownloadWindow(Ui_Download_Screen, QMainWindow):
    def __init__(self, MainWindow, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.MainWindowAttributes = MainWindow
        self.MainWindow = PythonDownloader()
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


# class for downloading a single video thread
class DownloadSingleVideo_Thread(QThread):
    ShowVideoTitle = Signal(str)
    Update_Gif = Signal(str)
    # will receive a arg for color style and the
    # text reference at UpdateUI_Status()
    Status_Text = Signal(str, str)
    Media_Home_Btns = Signal()

    def __init__(self, youtube_video, resolution_download, path, parent=None):
        super().__init__(parent)
        self.youtube_video = youtube_video
        self.resolution_download = resolution_download
        self.path = path
        self.DownloadWindow = DownloadWindow(self)

    def run(self):
        try:
            self.ShowVideoTitle.emit(f'{self.youtube_video.title}')

            self.Status_Text.emit("#2c2c2c", "[STATUS] : DOWNLOADING ... ")

            # optimal download if streams = None Type
            if not self.youtube_video.streams.filter(res=self.resolution_download, progressive=True, file_extension='mp4'):
                self.youtube_video.streams.filter(
                    progressive=True, file_extension='mp4').order_by(
                        'resolution'
                ).desc().first().download(f'{self.path}')
            else:
                self.youtube_video.streams.filter(
                    res=self.resolution_download,
                    file_extension='mp4',
                    progressive=True).first().download(f'{self.path}')

            # update gif when download is complete
            self.youtube_video.register_on_complete_callback(
                self.Update_Gif.emit(
                    ".\\designs\\bkp_ui\\../../imgs/sucess_gif.gif"
                )
            )
            self.Status_Text.emit(
                "#1aa839", "[SUCESS] : VIDEO DOWNLOADED SUCCESFULLY ! "
            )

            sleep(1.2)

        except Exception:
            self.Update_Gif.emit(
                ".\\designs\\bkp_ui\\../../imgs/error_gif.gif"
            )
            self.Status_Text.emit(
                "#7a1c15", "[ERROR] : NOT POSSIBLE TO DOWNLOAD  !  THE VIDEO PROBABLY IS NOT PUBLIC OR HAS AGE RESTRICTIONS OR IS UNAVAILABLE / BLOCKED BY REGION."
            )

        self.Media_Home_Btns.emit()


# thread used when download is a full playlist
class DownloadFP_Thread(QThread):
    ShowVideoTitle = Signal(str)
    Update_Gif = Signal(str)
    Status_Text = Signal(str, str)
    Media_Home_Btns = Signal()

    def __init__(self, youtube_video, resolution_download, path, QuantityVideos, parent=None):
        super().__init__(parent)
        self.youtube_video = youtube_video
        self.resolution_download = resolution_download
        self.path = path
        self.QuantityVideos = QuantityVideos
        self.DownloadWindow = DownloadWindow(self)
        self.SkippedVideos = []
        self.VideoCount = 1

    def run(self):
        # optimal download when stream is none
        for videos in self.youtube_video.videos:
            try:
                self.ShowVideoTitle.emit(
                    f'PLAYLIST : {self.youtube_video.title} - ({self.QuantityVideos} VIDEOS)'
                )
                self.Update_Gif.emit(
                    ".\\designs\\bkp_ui\\../../imgs/loading_gif.gif"
                )
                self.Status_Text.emit(
                    "#2c2c2c", f"[STATUS] : DOWNLOADING VIDEO {self.VideoCount} of {self.QuantityVideos} From PLAYLIST ... "
                )

                if not videos.streams.filter(res=self.resolution_download, progressive=True, file_extension='mp4'):
                    videos.streams.filter(
                        progressive=True, file_extension='mp4').order_by(
                            'resolution'
                    ).desc().first().download(f'{self.path}')
                else:
                    videos.streams.filter(
                        progressive=True, file_extension='mp4',
                        res=self.resolution_download).first().download(
                            f'{self.path}'
                    )

                videos.register_on_complete_callback(
                    self.Update_Gif.emit(
                        ".\\designs\\bkp_ui\\../../imgs/sucess_gif.gif"
                    )
                )
                self.VideoCount += 1
                videos.register_on_complete_callback(
                    self.Status_Text.emit(
                        "#1aa839", "[SUCESS] : VIDEOS DOWNLOADED SUCCESFULLY !"
                    )
                )

            # not interrupt an download in case of an error in a video
            except Exception:
                # get the videos that were skipped
                self.SkippedVideos.append(videos.title)
                continue

        self.Media_Home_Btns.emit()
        sleep(1.2)
        os.startfile(self.path)

        # shows videos that were skipped because of unavailability in youtube
        if self.SkippedVideos != []:
            self.Status_Text.emit(
                "#7a1c15", f"[INFO] : THE FOLLOWING VIDEO(S) WERE UNAVAILABLE TO DOWNLOAD : {self.SkippedVideos}"
            )


# thread used when download is a interval of a playlist
class DownloadIP_Thread(QThread):
    ShowVideoTitle = Signal(str)
    Update_Gif = Signal(str)
    Status_Text = Signal(str, str)
    Media_Home_Btns = Signal()

    def __init__(self, youtube_video, resolution_download, path, QuantityVideos, URL_Counter, List_Interval_URLS, Current_URL, Start, End, parent=None):
        super().__init__(parent)
        self.youtube_video = youtube_video
        self.resolution_download = resolution_download
        self.path = path
        self.QuantityVideos = QuantityVideos
        self.DownloadWindow = DownloadWindow(self)
        self.URL_Counter = URL_Counter
        self.List_Interval_URLS = List_Interval_URLS
        self.Current_URL = Current_URL
        self.Start = Start
        self.End = End
        self.SkippedVideos = []
        self.VideoCount = self.Start

    def run(self):
        # set a while loop based on counter to get
        # the url link from list counter as a string
        for self.URL_Counter in range(len(self.List_Interval_URLS)):
            try:
                self.Update_Gif.emit(
                    ".\\designs\\bkp_ui\\../../imgs/loading_gif.gif"
                )
                self.ShowVideoTitle.emit(
                    f'PLAYLIST : {self.youtube_video.title} - ({self.QuantityVideos} VIDEOS)'
                )
                self.Status_Text.emit(
                    f"#2c2c2c",
                    f"DOWNLOADING INTERVAL VIDEO {self.VideoCount} of {self.End} FROM PLAYLIST ..."
                )
                self.Current_URL = YouTube(
                    self.List_Interval_URLS[self.URL_Counter]
                )

                # optimal download when stream is none
                if not self.Current_URL.streams.filter(res=self.resolution_download, progressive=True, file_extension='mp4'):
                    self.Current_URL.streams.filter(
                        progressive=True, file_extension='mp4'
                    ).order_by('resolution').desc().first().download(
                        f'{self.path}'
                    )
                else:
                    self.Current_URL.streams.filter(
                        progressive=True, file_extension='mp4',
                        res=self.resolution_download).first().download(
                        f'{self.path}'
                    )  # download based on resolution choiced

                self.URL_Counter += 1
                self.Current_URL.register_on_complete_callback(
                    self.Update_Gif.emit(
                        ".\\designs\\bkp_ui\\../../imgs/sucess_gif.gif"
                    )
                )
                self.VideoCount += 1
                self.Current_URL.register_on_complete_callback(
                    self.Status_Text.emit(
                        "#1aa839", f"[SUCESS] : VIDEOS {self.Start} to {self.End} of PLAYLIST DOWNLOADED SUCCESFULLY ! "
                    )
                )

            # not interrupt an download in case of an error in a video
            except Exception:
                # get the videos that were skipped
                self.SkippedVideos.append(self.Current_URL.title)
                continue

        self.Media_Home_Btns.emit()
        sleep(1.2)
        os.startfile(self.path)

        # shows videos that were skipped because of unavailability in youtube
        if self.SkippedVideos != []:
            self.Status_Text.emit(
                "#7a1c15", f"[INFO] : THE FOLLOWING VIDEO(S) WERE UNAVAILABLE TO DOWNLOAD : {self.SkippedVideos}"
            )
            self.Current_URL.register_on_complete_callback(
                self.Update_Gif.emit(
                    ".\\designs\\bkp_ui\\../../imgs/sucess_gif.gif"
                )
            )


if __name__ == '__main__':
    qt = QApplication(sys.argv)
    App_main = PythonDownloader()
    App_main.show()
    qt.exec()
