from os import startfile

from PySide6.QtCore import QThread, Signal
from pytube import YouTube
from pytube.exceptions import MaxRetriesExceeded, VideoUnavailable

from .DownloadClass import DownloadWindow


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
        self.youtube_video: YouTube = youtube_video
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
                ).desc().first().download(
                    f'{self.path}', timeout=15, skip_existing=True, max_retries=1
                )
            else:
                self.youtube_video.streams.filter(
                    res=self.resolution_download,
                    file_extension='mp4',
                    progressive=True).first().download(
                        f'{self.path}', timeout=15, skip_existing=True, max_retries=1
                )

            # update gif when download is complete
            self.youtube_video.register_on_complete_callback(
                self.Update_Gif.emit(
                    ".\\designs\\bkp_ui\\../../imgs/sucess_gif.gif"
                )
            )
            self.Status_Text.emit(
                "#1aa839", "[SUCESS] : VIDEO DOWNLOADED SUCCESFULLY ! "
            )
            startfile(self.path)

        except MaxRetriesExceeded:
            self.Status_Text.emit(
                "#7a1c15", "[ERROR] : Timeout While Downloading.")
        except VideoUnavailable:
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
        self.youtube_video: YouTube = youtube_video
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
                    ).desc().first().download(
                        f'{self.path}', timeout=15, skip_existing=True, max_retries=1
                    )
                else:
                    videos.streams.filter(
                        progressive=True, file_extension='mp4',
                        res=self.resolution_download).first().download(
                            f'{self.path}', timeout=15, skip_existing=True, max_retries=1
                    )

                videos.register_on_complete_callback(
                    self.Update_Gif.emit(
                        ".\\designs\\bkp_ui\\../../imgs/sucess_gif.gif"
                    )
                )

                videos.register_on_complete_callback(
                    self.Status_Text.emit(
                        "#1aa839", "[SUCESS] : VIDEOS DOWNLOADED SUCCESFULLY !"
                    )
                )
                self.VideoCount += 1

            # not interrupt an download in case of an error in a video
            except MaxRetriesExceeded:
                self.Status_Text.emit(
                    "#7a1c15", "[ERROR] : Timeout While Downloading.")
            except VideoUnavailable:
                # get the videos that were skipped for some reason
                self.SkippedVideos.append(videos.title)
                continue

        self.Media_Home_Btns.emit()
        startfile(self.path)

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
        self.youtube_video: YouTube = youtube_video
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
                        f'{self.path}', timeout=15, skip_existing=True, max_retries=1
                    )
                else:
                    self.Current_URL.streams.filter(
                        progressive=True, file_extension='mp4',
                        res=self.resolution_download).first().download(
                        f'{self.path}', timeout=15, skip_existing=True, max_retries=1
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

            except MaxRetriesExceeded:
                self.Status_Text.emit(
                    "#7a1c15", "[ERROR] : Timeout While Downloading.")
            except VideoUnavailable:
                # get the videos that were skipped
                self.SkippedVideos.append(self.Current_URL.title)
                continue

        self.Media_Home_Btns.emit()
        startfile(self.path)

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
