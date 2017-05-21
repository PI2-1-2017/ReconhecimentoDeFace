# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QInputDialog, QLineEdit, QFileDialog

from threading import Thread

import qdarkstyle
import numpy as np
import cv2
import sys


# Adaptado de:
__author__ = "Nick Zanobini"
__version__ = "1.00"
__license__ = "GNU GPLv3"

guiLayout = uic.loadUiType("VideoFrameGui.ui")[0]


class VideoThreadClass(QtCore.QThread):

    newFrame = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, window_width, window_height, parent=None):
        super(VideoThreadClass, self).__init__(parent)
        
        # initialize the video camera stream
        self.stream = WebcamVideoStream(src=-1).start()
        
        # read the first frame from the stream
        self.frame = self.stream.read()
        
        # initialize the variable used to indicate if the thread should be stopped
        self.stopped = False
        self.window_height = window_height
        self.window_width = window_width

    def run(self):
        # keep looping infinitely until the thread is stopped
        while True:
            
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                
                # stop camera thread
                self.stream.stop()
                return

            # read the next frame from the stream
            self.frame = self.stream.read()
            
            # resize the frame to the size of the window
            img = cv2.resize(self.frame, (self.window_width, self.window_height), interpolation=cv2.INTER_CUBIC)
            
            # convert the color from cv2 to QImage format
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # get the dimensions of the image
            height, width, bpc = img.shape
            bpl = bpc * width
            
            # convert image to QImage 
            # QImage class provides a hardware-independent image representation that allows direct access to the pixel data, and can be used as a paint device
            image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            
            # emit signal from thread
            self.newFrame.emit(image)

    def stop(self):
        
        # indicate that the thread should be stopped
        self.stopped = True


class VideoFrame(QtWidgets.QWidget, guiLayout):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.running = False
        self.setupImgWindows()

        self.startButton.clicked.connect(self.start_clicked)
        #self.imageButton.clicked.connect(self.open_image)

        self.videoThread = VideoThreadClass(self.window_width, self.window_height)
        self.videoThread.start()
        self.videoThread.newFrame.connect(self.update_frame)

    # VidFrame is the name of the widget object in the .ui file.
    def update_frame(self, image):
        
        # display latest frame from video thread
        self.VidFrame.setImage(image)

    # Setup the video frame in the window according to the width and height definied in the .ui file.
    def setupImgWindows(self):
        self.window_width = self.VidFrame.frameSize().width()
        self.window_height = self.VidFrame.frameSize().height()
        self.VidFrameGUI = self.VidFrame
        self.VidFrame = VideoWidget(self.VidFrame)
        self.VidFrame.hide()

    def start_clicked(self):
        self.running = not self.running
        if self.running:
            self.startButton.setText('Parar Busca')
            self.VidFrame.show()
        else:
            self.startButton.setText('Iniciar Busca')
            self.VidFrame.hide()

    #def open_image(self):
        # Image code goes here.
 
    def closeEvent(self, event):
        self.running = False
        self.videoThread.stop()
        self.close()
        sys.exit()


class VideoWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qtPainter = QtGui.QPainter()
        qtPainter.begin(self)
        if self.image:
            qtPainter.drawImage(QtCore.QPoint(0, 0), self.image)
        qtPainter.end()


class WebcamVideoStream:
    def __init__(self, src=-1):
        
        # initialize the video camera stream and read the first frame from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should be stopped
        self.stopped = False

    def start(self):
        
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        
        return self

    def update(self):
        
        # keep looping infinitely until the thread is stopped
        while True:
           
           # if the thread indicator variable is set, stop the thread
            if self.stopped:
                
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        
        # return the frame most recently read
        return self.frame

    def stop(self):
        
        # indicate that the thread should be stopped
        self.stopped = True

app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
window = VideoFrame(None)
window.setWindowTitle('Buscar Alvo')
window.show()

app.exec_()