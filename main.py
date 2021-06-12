
from gui import Ui_MainWindow
import DatabaseFunctions_v2 as df 
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog  ,QApplication ,QDialog ,QWidget ,QLabel
from PyQt5.QtGui import  QPixmap
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QDir, Qt, QUrl, QSize
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, 
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar)
class VideoPlayer(QWidget):

    def __init__(self,fileName,parent=None):
        super(VideoPlayer, self).__init__(parent)
        self.btnSize = QSize(16, 16)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))

        self.videoWidget = QVideoWidget()
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(self.btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        self.playButton.setEnabled(True)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
       
        
        self.controlLayout = QHBoxLayout()
        self.controlLayout.setContentsMargins(0, 0, 0, 0)
        self.controlLayout.addWidget(self.playButton)
        self.controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)
        layout.addLayout(self.controlLayout)

        self.setLayout(layout)



    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()  
    
    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)



class Main(QtWidgets.QMainWindow ,Ui_MainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.label=QLabel()
        self.player= None
        self.search_list = []
        self.media_path =None
        self.current_media =None
        self.ui.image_load_pushButton_2.clicked.connect(self.click_load_image)
        self.ui.video_load_pushButton_2.clicked.connect(self.click_load_video)
        self.ui.histogram_pushButton_2.clicked.connect(self.search_hist_btn_function)
        self.ui.colorLayout_pushButton_2.clicked.connect(self.search_layout_btn_function)
        self.ui.meanColor_pushButton_2.clicked.connect(self.search_mean_btn_function)
        self.ui.Back_pushButton.clicked.connect(self.Back_button)
        
        self.ui.insert_pushButton_2.clicked.connect(self.add_to_database_btn)
        self.ui.video_search_pushButton_2.clicked.connect(self.search_video_function)

    def search_video_function(self):
        if self.current_media == 1:
            for i in reversed(range(self.ui.gridLayout_display_images.count())): 
                self.ui.gridLayout_display_images.itemAt(i).widget().setParent(None)

            self.ui.stackedWidget.setCurrentIndex(1)

            player = VideoPlayer(self.media_path)
            self.ui.gridLayout_display_images.addWidget(player,0,0,1,3,Qt.AlignCenter)

            paths = df.retrive_similiar_videos(self.media_path,0.215,0.7)
            # print(paths)
            # print("finished")
            if paths:
                i = 1
                j = 0
                for path in paths:
                    player = VideoPlayer(path)
                    self.ui.gridLayout_display_images.addWidget(player,i,j,Qt.AlignCenter)
                    j += 1
                    if j == 3:
                        j = 0
                        i += 1

        
    def Back_button(self) :
        self.ui.stackedWidget.setCurrentIndex(0)


    def click_load_image(self):

        fileName, _ = QFileDialog.getOpenFileName(self, "Choose Image File", "",
                                                "Image Files (*.jpg *.png *.jpeg *.ico);;All Files (*)")
        if fileName != '':
            self.media_path = fileName
            pixmap= QPixmap(self.media_path)
            scaled = pixmap.scaled(self.label.size())
            self.label.setPixmap(scaled)
            self.label.setScaledContents(True)
            self.label.setPixmap(scaled)
            for i in reversed(range(self.ui.add_verticalLayout.count())): 
                 self.ui.add_verticalLayout.itemAt(i).widget().setParent(None)
            self.ui.add_verticalLayout.addWidget(self.label)
            self.current_media = 0
        
    def click_load_video(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Choose Video File",
                ".", "Video Files (*.mp4 *.flv *.ts *.mts *.avi)")

        if fileName != '':
            self.media_path = fileName
            self.player = VideoPlayer(fileName)
            for i in reversed(range(self.ui.add_verticalLayout.count())): 
                 self.ui.add_verticalLayout.itemAt(i).widget().setParent(None)
            self.ui.add_verticalLayout.addWidget(self.player)
            self.current_media = 1


       
    def search_mean_btn_function (self):
        if self.current_media == 0:
            for i in reversed(range(self.ui.gridLayout_display_images.count())): 
                self.ui.gridLayout_display_images.itemAt(i).widget().setParent(None)
            self.ui.stackedWidget.setCurrentIndex(1)
            # print(self.media_path)
            self.search_list = df.retrieve_using_mean(self.media_path)
            i =1
            j=0
            label=QLabel()
            pixmap= QPixmap(self.media_path)
            scaled = pixmap.scaled(QSize(200,200))
            label.setPixmap(scaled)
            self.ui.gridLayout_display_images.addWidget(label,0,0,1,6,Qt.AlignCenter)

            if self.search_list:
                for x in self.search_list:
                    
                    label=QLabel()
                    pixmap= QPixmap(x[0])
                    scaled = pixmap.scaled(QSize(200,200))
                    label.setPixmap(scaled)
                    self.ui.gridLayout_display_images.addWidget(label,i,j,Qt.AlignCenter)

                    j+=1
                    if j ==6:
                        j=0
                        i+=1

   
    def search_layout_btn_function (self):
        if self.current_media == 0:
            for i in reversed(range(self.ui.gridLayout_display_images.count())): 
                self.ui.gridLayout_display_images.itemAt(i).widget().setParent(None)
            self.ui.stackedWidget.setCurrentIndex(1)
            self.search_list = df.retrieve_using_layout(self.media_path)
        
            # print(self.search_list)
            i =1
            j=0
            label=QLabel()
            pixmap= QPixmap(self.media_path)
            scaled = pixmap.scaled(QSize(200,200))
            label.setPixmap(scaled)
            self.ui.gridLayout_display_images.addWidget(label,0,0,1,6,Qt.AlignCenter)
            if self.search_list:
                for x in self.search_list:
                
                    label=QLabel()
                    pixmap= QPixmap(x)
                    scaled = pixmap.scaled(QSize(200,200))
                    label.setPixmap(scaled)
                    self.ui.gridLayout_display_images.addWidget(label,i,j,Qt.AlignCenter)

                    j+=1
                    if j ==6:
                        j=0
                        i+=1


    #error
    def search_hist_btn_function (self):
        if self.current_media == 0:
            for i in reversed(range(self.ui.gridLayout_display_images.count())): 
                self.ui.gridLayout_display_images.itemAt(i).widget().setParent(None)
            self.ui.stackedWidget.setCurrentIndex(1)
            self.search_list = df.retrieve_using_histo(self.media_path)
            i =1
            j=0
            label=QLabel()
            pixmap= QPixmap(self.media_path)
            scaled = pixmap.scaled(QSize(200,200))
            label.setPixmap(scaled)
            self.ui.gridLayout_display_images.addWidget(label,0,0,1,6,Qt.AlignCenter)
            if self.search_list:
                for x in self.search_list:
                
                    label=QLabel()
                    pixmap= QPixmap(x)
                    scaled = pixmap.scaled(QSize(200,200))
                    label.setPixmap(scaled)
                    self.ui.gridLayout_display_images.addWidget(label,i,j,Qt.AlignCenter)

                    j+=1
                    if j ==6:
                        j=0
                        i+= 1

    def add_to_database_btn (self): 
        if self.current_media ==0:
            # print(self.media_path)
            df.insertInDB(self.media_path) 
        else:
            df.insert_video_DB(self.media_path)
            



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)  
    MainWindow=Main()
    MainWindow.show()
    sys.exit(app.exec_())

