from designs.design_Main import *
from designs.design_Options import *
from designs.design_Download import *
from PySide6.QtWidgets import QMainWindow,QApplication,QFileDialog
from PySide6.QtGui import QPixmap,QImage,QMovie
from PySide6.QtCore import QThread,Signal,Qt
import os
from pytube import YouTube,Playlist
import sys
import re
import time
import requests

class PythonDownloader(QMainWindow,Ui_PytubeDownloader):
    def __init__(self,parent = None):
        super().__init__(parent)
        super().setupUi(self)
        self.setFixedSize(800,600)
        self.OptionsWindow = None
        self.btnDownloadOptions.hide()
        self.Type_of_URL = ''
        self.Quantity_of_Videos = ''
        self.Video_URL = ''
        self.Video_Title = ''
        self.url_info.setText("Copie e Cole o Link do Video ou da Playlist Aqui :")
        self.Thumb_Image = QImage()

        self.btnSearchVideo.clicked.connect(self.SearchVideoURL) # search video function
        self.btnDownloadOptions.clicked.connect(self.Open_Options_Window) # second window function

        python_gif = QtGui.QMovie(".\\designs\\bkp_ui\\../../imgs/pythongif.gif") # set python gif to the screen
        self.python_ico.setMovie(python_gif)
        python_gif.start()

        github_gif = QtGui.QMovie(".\\designs\\bkp_ui\\../../imgs/github_gif.gif") # set github gif to the screen
        self.githubgif.setMovie(github_gif)
        github_gif.start()

        self.txtgithub.setOpenExternalLinks(True)
        self.txtgithub.setText("<a href='https://github.com/bryanoliveira11'>GitHub</a>")


    def SearchVideoURL(self): # search video and validate re
        self.VIDEO_RE = r'^(http(s):\/\/.)[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$' # re for videos
        self.PLAYLIST_RE = r'^https?:\/\/(www.youtube.com|youtube.com)\/playlist(.*)$' # re for playlist
        
        self.Video_URL = str(self.Url_Input.text()).strip().replace(' ','') # URL inputed by user
        self.Url_Input.setText('')

        try: 
            if re.match(self.PLAYLIST_RE,self.Video_URL):
                self.Type_of_URL = 'PLAYLIST'

            elif re.match(self.VIDEO_RE,self.Video_URL):
                self.Type_of_URL = 'VIDEO'
            
            self.getUrl_Content()
            self.ScreenSearchDefaults()

        except Exception:
            self.Url_Exception.setText(f'[ERRO] : Não Foi Possível Encontrar a URL. Tente Novamente ! <br/> O Video/Playlist Talvez Esteja Privado.')
            self.Url_Exception.setAlignment(Qt.AlignCenter)
            self.HideVideoContent()


    def getUrl_Content(self):   # that function will get the videos title and thumbnail. Also, will set Playlist for playlist and Youtube for video url

        if not self.Type_of_URL == 'PLAYLIST': # setting title and thumbnail when playlist url
            
            self.Youtube_Video = YouTube(self.Video_URL) # setting title and thumbnail when video url
            Url_ThumbNail = self.Youtube_Video.thumbnail_url # get the thumbnail url
            self.Quantity_of_Videos = 1

        else:
            self.Youtube_Video = Playlist(self.Video_URL)
            Url_ThumbNail = YouTube(self.Youtube_Video.video_urls[0]).thumbnail_url # this will get the first video thumbnail url, playlists doesnt have thumbnail url :c
            self.Quantity_of_Videos = self.Youtube_Video.length # get the amount of videos in the playlist

        self.Video_Title = str(self.Youtube_Video.title).upper().strip() # prevent user from using spaces in the url
        self.video_title.setText(f'{self.Video_Title}') # setting the title
        self.Thumb_Image.loadFromData(requests.get(Url_ThumbNail).content) # getting the thumbnail url and its content with requests
        self.video_thumb.setPixmap(QPixmap(self.Thumb_Image).scaledToWidth(303))
        self.video_thumb.setAlignment(Qt.AlignCenter)


    def ScreenSearchDefaults(self): # that function will display the next button, and display the type of url and the quantity of video
        self.Url_Exception.setText('')
        self.btnDownloadOptions.show()
        self.video_type.setText(f'TIPO : {self.Type_of_URL}')
        self.video_qtd.setText(f'QUANTIDADE : {self.Quantity_of_Videos}')


    def HideVideoContent(self): # hide things in main screen.
        self.video_title.setText('') 
        self.video_type.setText('')
        self.video_qtd.setText('')
        self.video_thumb.setPixmap(QPixmap(''))
        self.btnDownloadOptions.hide()


    def Open_Options_Window(self): # open the options window and close the main
        if self.OptionsWindow is None:
            self.OptionsWindow = OptionsWindow(self)
        self.hide()
        self.OptionsWindow.show()


class OptionsWindow(Ui_DownloaderOptions,QMainWindow):
    def __init__(self ,MainWindow, parent = None):
        super().__init__(parent)
        super().setupUi(self)
        self.MainWindowAttributes = MainWindow
        self.setFixedSize(800,600)
        self.DownloadWindow = None

        self.app_title.setText("OPÇÕES DE DOWNLOAD")
        self.Play_Text.setText("OPÇÕES - PLAYLIST")
        self.Res_text.setText("RESOLUÇÃO")
        self.D_Full.setText(f"Playlist Inteira {self.MainWindowAttributes.Quantity_of_Videos} Videos")
        self.D_Interval.setText("Intervalo")
        self.D_Path_Text.setText("PASTA DESTINO")
        self.End_Num.setPlaceholderText(" num final")
        self.Start_Num.setPlaceholderText("num inicial")

        loading_gif = QtGui.QMovie(".\\designs\\bkp_ui\\../../imgs/options_gif.gif") # set gif to the screen
        self.optionsIcon.setMovie(loading_gif)
        loading_gif.start()
        
        # resolutions and playlist lists / function to validate all
        self.Resolutions_List = [self.Res_1080p,self.Res_720p,self.Res_480p,self.Res_360p]
        self.Playlist_OptionsList = [self.D_Full,self.D_Interval]
        self.Playlist_InputsList = [self.End_Num,self.Start_Num]

        # get the methods to work on that class
        self.getvideoTitleThumbnail()
        self.Checkboxes_Validation()
        self.DisablePlaylistWhenVideo()
        self.getDownloadPathFromTxt()
        self.btnBackMain.clicked.connect(self.BacktoMainWindow)
        self.btnSearchFolder.clicked.connect(self.SelectDownload_Path)
        self.btnDownload.clicked.connect(self.StartDownloadValidations)


    def BacktoMainWindow(self): # function to get back to the first window when button is clicked.
        self.hide()
        self.MainWindow = PythonDownloader()
        self.MainWindow.show()


    def getvideoTitleThumbnail(self): # this functions will get the thumb and title from the other class aka main window
        self.video_thumb_opt.setPixmap(QPixmap(self.MainWindowAttributes.Thumb_Image).scaledToWidth(360))
        self.video_thumb_opt.setAlignment(Qt.AlignCenter)

        if not self.MainWindowAttributes.Type_of_URL == 'PLAYLIST':
            self.video_title_opt.setText(self.MainWindowAttributes.Video_Title)
        else:
            self.video_title_opt.setText(f'{self.MainWindowAttributes.Video_Title} - ( {self.MainWindowAttributes.Quantity_of_Videos} VIDEOS )')

        self.video_title_opt.setAlignment(Qt.AlignCenter)


    def DisablePlaylistWhenVideo(self): # will disable the checkboxes when the download is a single video
        if self.MainWindowAttributes.Type_of_URL == 'VIDEO':
            for option_boxes in self.Playlist_OptionsList:
                option_boxes.setEnabled(False)

            for option_inputs in self.Playlist_InputsList:
                option_inputs.setEnabled(False)


    def Checkboxes_Validation(self): # set a connect state changed event to validate what checkbox is checked by user at options screen
        
         # default None to the variables for later validations
        self.Resolution_Download = None 
        self.Playlist_Download = None 

        for Resolutions in self.Resolutions_List: # get all checkboxes from Resolutions_List and set the function
            Resolutions.clicked.connect(self.ValidateResolution_CheckBoxes)
        
        for PlaylistOption in self.Playlist_OptionsList: # get all checkboxes from Playlist_OptionsList and set the function
            PlaylistOption.clicked.connect(self.ValidatePlaylist_CheckBoxes)


    def ValidateResolution_CheckBoxes(self): # change the checked boxes by sender validation ; Resolutions
        try:

            for Res in range (len(self.Resolutions_List)):

                self.currentResCheckbox = self.Resolutions_List[Res]

                if self.currentResCheckbox.isChecked() and self.currentResCheckbox != self.sender():
                    self.currentResCheckbox.setChecked(False)

                SelectedRes = {
                    self.Res_1080p.isChecked():'1080p',
                    self.Res_720p.isChecked():'720p',
                    self.Res_480p.isChecked():'480p',
                    self.Res_360p.isChecked():'360p',
                }

            self.Resolution_Download = SelectedRes[True]

        except KeyError:           
            self.Resolution_Download = None
            return
    

    def ValidatePlaylist_CheckBoxes(self): # change the checked boxes by Qt.Checked sender validation ; Playlist Options

        try:

            for PlaylistOptions in range(len(self.Playlist_OptionsList)):

                self.currentPlaylistCheckbox = self.Playlist_OptionsList[PlaylistOptions]

                if self.currentPlaylistCheckbox.isChecked() and self.currentPlaylistCheckbox != self.sender():
                    self.currentPlaylistCheckbox.setChecked(False)

                SelectedPlaylistOption = {
                    self.D_Full.isChecked():'Full Playlist',
                    self.D_Interval.isChecked():'Interval Videos',
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
        
        
    def OpenDownloadWindow(self): # opens the download window
        if self.DownloadWindow is None:
            self.DownloadWindow = DownloadWindow(self)
        self.hide()
        self.DownloadWindow.show()
        
        
    def SelectDownload_Path(self): # functions to select a folder for downloads and create a txt to save it

        self.Download_Folder = QFileDialog.getExistingDirectory()
        self.path_show.setEnabled(True)
        self.path_show.setText(self.Download_Folder)
        self.Download_Exception.setText('')
        
        with open('DownloadPath.txt','w') as DownloadPath: # will create a txt file and save the folder inside
            if not self.Download_Folder:
                self.path_show.setText('[INFO] : Seu Caminho Para Download Está Vázio ! ')
                return
            
            DownloadPath.write(self.Download_Folder)


    def getDownloadPathFromTxt(self): # that function will open the txt DownloadPath and get the path thats on it to show at screen.
        try:
            with open('DownloadPath.txt') as readPath: # get last saved path from DownloadPath.txt and show at the screen, user can change any moment
                self.path_show.setText(readPath.read())  
        except FileNotFoundError:
            self.Download_Exception.setText('[INFO] : Escolha Uma Pasta Para Salvar Seus Videos Antes the Começar a Baixar !')


    def StartDownloadValidations(self):
        try:
            with open('DownloadPath.txt') as readPath: # try to read the path to download and return a error if there is none
                self.Path = readPath.read()
                if self.Path == '':
                    self.Download_Exception.setText('[INFO] : Escolha Uma Pasta Para Salvar Seus Videos Antes the Começar a Baixar !')
                    return

        except FileNotFoundError:
            self.Download_Exception.setText('[INFO] : Escolha Um Caminho Para Salvar os Videos !')
            return
        
        if self.MainWindowAttributes.Type_of_URL == 'PLAYLIST' and self.Playlist_Download == None or self.Resolution_Download == None:
            self.Download_Exception.setText('[INFO] : Marque as Configurações do Video Corretamente Antes de Baixar !')
            return

        if not self.MainWindowAttributes.Type_of_URL == 'PLAYLIST' and self.Resolution_Download != None: 
            self.DownloadSingleVideo()
        
        if self.D_Full.isChecked() and self.Resolution_Download != None:
            self.DownloadFullPlaylist() # calls function to playlist download

        if self.D_Interval.isChecked() and self.Resolution_Download != None:
            self.ValidateInputs_Interval()
        
        
    def DownloadSingleVideo(self): # Function to download a single video, it calls the SV Thread and uses the connect to update the UI with text and gif status
        self.OpenDownloadWindow()
        self.DownloadSV_Thread = DownloadSingleVideo_Thread(self.MainWindowAttributes.Youtube_Video, self.Resolution_Download, self.Path)
        self.DownloadSV_Thread.ShowVideoTitle.connect(self.DownloadWindow.UpdateUI_Title)
        self.DownloadSV_Thread.Update_Gif.connect(self.DownloadWindow.UpdateUI_GIFS)
        self.DownloadSV_Thread.Status_Text.connect(self.DownloadWindow.UpdateUI_Status)
        self.DownloadSV_Thread.Media_Home_Btns.connect(self.DownloadWindow.UpdateUI_ShowBtns)
        self.DownloadSV_Thread.start()


    def DownloadFullPlaylist(self): # function to download full playlist calls a DownloadFP_Thread thread
        self.OpenDownloadWindow()
        self.DownloadFP_Thread = DownloadFP_Thread(self.MainWindowAttributes.Youtube_Video,self.Resolution_Download,self.Path,self.MainWindowAttributes.Quantity_of_Videos)
        self.DownloadFP_Thread.ShowVideoTitle.connect(self.DownloadWindow.UpdateUI_Title)
        self.DownloadFP_Thread.Update_Gif.connect(self.DownloadWindow.UpdateUI_GIFS)
        self.DownloadFP_Thread.Status_Text.connect(self.DownloadWindow.UpdateUI_Status)
        self.DownloadFP_Thread.Media_Home_Btns.connect(self.DownloadWindow.UpdateUI_ShowBtns)
        self.DownloadFP_Thread.start()
        

    def DownloadIntervalPlaylist(self): #function to download interval videos of a playlist calls a DownloadIP_Thread thread
        self.OpenDownloadWindow()
        self.DownloadIP_Thread = DownloadIP_Thread(self.MainWindowAttributes.Youtube_Video,self.Resolution_Download,self.Path,self.MainWindowAttributes.Quantity_of_Videos,self.URL_Counter,self.List_Interval_URLS,self.Current_URL,self.StartInterval,self.EndInterval)
        self.DownloadIP_Thread.ShowVideoTitle.connect(self.DownloadWindow.UpdateUI_Title)
        self.DownloadIP_Thread.Update_Gif.connect(self.DownloadWindow.UpdateUI_GIFS)
        self.DownloadIP_Thread.Status_Text.connect(self.DownloadWindow.UpdateUI_Status)
        self.DownloadIP_Thread.Media_Home_Btns.connect(self.DownloadWindow.UpdateUI_ShowBtns)
        self.DownloadIP_Thread.start()


    def ValidateInputs_Interval(self):
        try:
            self.StartInterval = int(self.Start_Num.text()) # user start and end inputs
            self.EndInterval = int(self.End_Num.text())
            self.ListAll_URLS = ([0,*self.MainWindowAttributes.Youtube_Video.video_urls]) # list of all urls in the playlist

            self.Current_URL = None # it will save the current URL in the loop 
            self.URL_Counter = 0 # counter starts at 0
            self.List_Interval_URLS = self.ListAll_URLS[self.StartInterval:self.EndInterval+1]

            if self.StartInterval > self.EndInterval or self.StartInterval > self.MainWindowAttributes.Quantity_of_Videos or self.EndInterval > self.MainWindowAttributes.Quantity_of_Videos or self.StartInterval < 0 or self.EndInterval < 0 or self.StartInterval == 0 or self.EndInterval == 0:
                self.Download_Exception.setText(f"[INFO] : Use Somente Números Maiores Que 0 e até {self.MainWindowAttributes.Quantity_of_Videos} ! O Número Inicial Deve Ser Menor Que o Final ")
                self.Start_Num.setText('')
                self.End_Num.setText('')
            elif self.StartInterval == self.EndInterval:
                self.Download_Exception.setText(f"[INFO] : O Número Inicial e o Final Devem Ser Diferentes ! ")
                self.End_Num.setText('')
            else:
                self.DownloadIntervalPlaylist()

        except ValueError:
            self.Download_Exception.setText(f"[INFO] : Digite Apenas Números ! ")
            self.Start_Num.setText('')
            self.End_Num.setText('')


class DownloadWindow(Ui_Download_Screen,QMainWindow):
    def __init__(self ,MainWindow, parent = None):
        super().__init__(parent)
        super().setupUi(self)
        self.MainWindowAttributes = MainWindow
        self.MainWindow = PythonDownloader()
        self.setFixedSize(800,575)
        self.UpdateStatusGif(".\\designs\\bkp_ui\\../../imgs/loading_gif.gif")
        self.btnMediaPlayer.hide()
        self.btnHome.hide()
        self.btnHome.clicked.connect(self.BacktoHome) # return to main window
        self.btnMediaPlayer.clicked.connect(lambda: os.startfile(self.MainWindowAttributes.Path)) # open the path file


    def UpdateStatusGif(self, gif_path):
        loading_gif = QtGui.QMovie(gif_path)
        self.Status_gif.setMovie(loading_gif)
        loading_gif.start()

    def BacktoHome(self):
        self.hide()
        self.MainWindow.show()

    def UpdateUI_Title(self,title): # function to update the ui with the signal from the Qthread
        self.VideoTitle.setText(title)
        self.VideoTitle.setAlignment(Qt.AlignCenter)
        

    def UpdateUI_Status(self,color,status): # function that updates the status message
        self.StatusMessage.setText(status)
        self.StatusMessage.setAlignment(Qt.AlignCenter)
        self.StatusMessage.setStyleSheet(f"font: 75 11pt;Segoe UI;font-weight: 700;margin-left: 2px;color:{color}")


    def UpdateUI_GIFS(self,gif_path): # function that updates the status gif
        self.UpdateStatusGif(gif_path)


    def UpdateUI_ShowBtns(self): # will emit a signal to show the btns after download
        self.btnHome.show()
        self.btnMediaPlayer.show()
        self.txthome.setText('ÍNICIO')
        self.txtpath.setText('ABRIR')
        

class DownloadSingleVideo_Thread(QThread): # class for downloading a single video thread
    ShowVideoTitle  = Signal(str)
    Update_Gif = Signal(str)
    Status_Text = Signal(str,str) # will receive a arg for color style and the text reference at UpdateUI_Status()
    Media_Home_Btns = Signal()

    def __init__(self, youtube_video, resolution_download, path,parent=None):
        super().__init__(parent)
        self.youtube_video = youtube_video
        self.resolution_download = resolution_download
        self.path = path
        self.DownloadWindow = DownloadWindow(self)


    def run(self):
        try:
            self.ShowVideoTitle.emit(f'{self.youtube_video.title}')

            self.Status_Text.emit("#2c2c2c",f"[STATUS] : BAIXANDO ... ")

            if not self.youtube_video.streams.filter(res=self.resolution_download,progressive=True,file_extension='mp4'): # optimal download if streams = None Type
                self.youtube_video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(f'{self.path}')
            else:
                self.youtube_video.streams.filter(res=self.resolution_download,file_extension='mp4',progressive=True).first().download(f'{self.path}')
                
            self.youtube_video.register_on_complete_callback(self.Update_Gif.emit(".\\designs\\bkp_ui\\../../imgs/sucess_gif.gif")) # update gif when download is complete
            self.Status_Text.emit("#1aa839","[SUCESSO] : SEUS VIDEOS FORAM BAIXADOS ! ")

            time.sleep(1.2)

        except Exception:
            self.Update_Gif.emit(".\\designs\\bkp_ui\\../../imgs/error_gif.gif")
            self.Status_Text.emit("#7a1c15","[ERRO] : NÃO FOI POSSÍVEL BAIXAR !  O VIDEO PROVAVELMENTE ESTÁ : PRIVADO, POSSUÍ RESTRIÇÕES DE IDADE, ESTÁ INDISPONÍVEL / BLOQUEADO NA SUA REGIÃO.")
            
        self.Media_Home_Btns.emit()


class DownloadFP_Thread(QThread): # thread used when download is a full playlist
    ShowVideoTitle  = Signal(str)
    Update_Gif = Signal(str)
    Status_Text = Signal(str,str) 
    Media_Home_Btns = Signal()

    def __init__(self, youtube_video, resolution_download, path,QuantityVideos,parent=None):
        super().__init__(parent)
        self.youtube_video = youtube_video
        self.resolution_download = resolution_download
        self.path = path
        self.QuantityVideos = QuantityVideos
        self.DownloadWindow = DownloadWindow(self)
        self.SkippedVideos = []
        self.VideoCount = 1

    def run(self):

        for videos in self.youtube_video.videos: # optimal download when stream is none
            try:
                self.ShowVideoTitle.emit(f'PLAYLIST : {self.youtube_video.title} - ({self.QuantityVideos} VIDEOS)')
                self.Update_Gif.emit(".\\designs\\bkp_ui\\../../imgs/loading_gif.gif")
                self.Status_Text.emit("#2c2c2c",f"[STATUS] : BAIXANDO VIDEO {self.VideoCount} de {self.QuantityVideos} DA PLAYLIST ... ")
        
                if not videos.streams.filter(res=self.resolution_download,progressive=True,file_extension='mp4'):
                    videos.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(f'{self.path}')
                else:
                    videos.streams.filter(progressive=True, file_extension='mp4',res=self.resolution_download).first().download(f'{self.path}')
                
                videos.register_on_complete_callback(self.Update_Gif.emit(".\\designs\\bkp_ui\\../../imgs/sucess_gif.gif")) 
                self.VideoCount += 1
                videos.register_on_complete_callback(self.Status_Text.emit("#1aa839","[SUCESSO] : OS VIDEOS FORAM BAIXADOS ! "))

            except Exception: # not interrupt an download in case of an error in a video
                self.SkippedVideos.append(videos.title) # get the videos that were skipped
                continue

        self.Media_Home_Btns.emit()
        time.sleep(1.2)
        os.startfile(self.path)

        if self.SkippedVideos != []: # shows videos that were skipped because of unavailability in youtube
            self.Status_Text.emit("#7a1c15",f"[INFO] : OS SEGUINTES VIDEOS ESTAVAM INDISPONÍVEIS PARA BAIXAR : {self.SkippedVideos}")
        


class DownloadIP_Thread(QThread): # thread used when download is a interval of a playlist
    ShowVideoTitle  = Signal(str)
    Update_Gif = Signal(str)
    Status_Text = Signal(str,str) 
    Media_Home_Btns = Signal()

        
    def __init__(self, youtube_video, resolution_download, path,QuantityVideos,URL_Counter,List_Interval_URLS,Current_URL,Start,End,parent=None):
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
        
        for self.URL_Counter in range (len(self.List_Interval_URLS)): # set a while loop based on counter to get the url link from list counter as a string
            try:
                
                self.Update_Gif.emit(".\\designs\\bkp_ui\\../../imgs/loading_gif.gif")
                self.ShowVideoTitle.emit(f'PLAYLIST : {self.youtube_video.title} - ({self.QuantityVideos} VIDEOS)')
                self.Status_Text.emit(f"#2c2c2c",f"BAIXANDO INTERVALO {self.VideoCount} de {self.End} DA PLAYLIST ...")

                self.Current_URL = YouTube(self.List_Interval_URLS[self.URL_Counter])

                if not self.Current_URL.streams.filter(res=self.resolution_download,progressive=True,file_extension='mp4'): # optimal download when stream is none
                    self.Current_URL.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(f'{self.path}') 
                else:
                    self.Current_URL.streams.filter(progressive=True, file_extension='mp4',res=self.resolution_download).first().download(f'{self.path}') # download based on resolution choiced

                self.URL_Counter += 1

                self.Current_URL.register_on_complete_callback(self.Update_Gif.emit(".\\designs\\bkp_ui\\../../imgs/sucess_gif.gif")) 
                self.VideoCount += 1
                self.Current_URL.register_on_complete_callback(self.Status_Text.emit("#1aa839",f"[SUCESS] : OS VIDEOS de {self.Start} a {self.End} da PLAYLIST FORAM BAIXADOS ! "))

            except Exception: # not interrupt an download in case of an error in a video
                self.SkippedVideos.append(self.Current_URL.title) # get the videos that were skipped
                continue
        
        self.Media_Home_Btns.emit()
        time.sleep(1.2)
        os.startfile(self.path)

        if self.SkippedVideos != []: # shows videos that were skipped because of unavailability in youtube
            self.Status_Text.emit("#7a1c15",f"[INFO] : OS SEGUINTES VIDEOS ESTAVAM INDISPONÍVEIS PARA BAIXAR : {self.SkippedVideos}")
            self.Current_URL.register_on_complete_callback(self.Update_Gif.emit(".\\designs\\bkp_ui\\../../imgs/sucess_gif.gif")) 


if __name__ == '__main__':
    qt = QApplication(sys.argv)
    App_main = PythonDownloader()
    App_main.show()
    qt.exec()