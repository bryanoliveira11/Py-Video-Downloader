import re

import requests
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QMovie, QPixmap
from PySide6.QtWidgets import QMainWindow
from pytube import Playlist, YouTube
from pytube.exceptions import RegexMatchError, VideoUnavailable

from designs.design_Main import Ui_PytubeDownloader

from .OptionsClass import OptionsWindow


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

        try:
            if re.match(self.PLAYLIST_RE, self.Video_URL):
                self.Type_of_URL = 'PLAYLIST'

            elif re.match(self.VIDEO_RE, self.Video_URL):
                self.Type_of_URL = 'VIDEO'

            self.getUrl_Content()
            self.ScreenSearchDefaults()

        except (RegexMatchError, VideoUnavailable):
            self.Url_Exception.setText(
                '[ERROR] : Not Possible to Search the URL. Try Again ! <br/> \
                Make Sure that the Video/Playlist is not Private.'
            )
            self.Url_Exception.setAlignment(Qt.AlignCenter)
            self.Url_Input.setText('')
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
