import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
import os
import time

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0)
        while True:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)

class FingerSpellingCollector(QWidget):

    def initData(self):
        self.collectionTarget = [
            {'key' : 'ㄱ', 'english' : 'giyeok'}, 
            {'key' : 'ㄴ', 'english' : 'nieun'}, 
            {'key' : 'ㄷ', 'english' : 'digeut'}, 
            {'key' : 'ㄹ', 'english' : 'rieul'}, 
            {'key' : 'ㅁ', 'english' : 'mieum'}, 
            {'key' : 'ㅂ', 'english' : 'bieup'}, 
            {'key' : 'ㅅ', 'english' : 'siot'}, 
            {'key' : 'ㅇ', 'english' : 'ieung'}, 
            {'key' : 'ㅈ', 'english' : 'jieut'}, 
            {'key' : 'ㅊ', 'english' : 'chieut'}, 
            {'key' : 'ㅋ', 'english' : 'kieuk'}, 
            {'key' : 'ㅌ', 'english' : 'tieut'}, 
            {'key' : 'ㅍ', 'english' : 'pieup'}, 
            {'key' : 'ㅎ', 'english' : 'hieut'}, 
            {'key' : 'ㅏ', 'english' : 'a'}, 
            {'key' : 'ㅑ', 'english' : 'ya'}, 
            {'key' : 'ㅓ', 'english' : 'eo'}, 
            {'key' : 'ㅕ', 'english' : 'yeo'}, 
            {'key' : 'ㅗ', 'english' : 'o'}, 
            {'key' : 'ㅛ', 'english' : 'yo'}, 
            {'key' : 'ㅜ', 'english' : 'u'}, 
            {'key' : 'ㅠ', 'english' : 'yu'}, 
            {'key' : 'ㅡ', 'english' : 'eu'}, 
            {'key' : 'ㅣ', 'english' : 'i'}, 
            {'key' : 'ㅔ', 'english' : 'e'}, 
            {'key' : 'ㅖ', 'english' : 'ye'}, 
            {'key' : 'ㅐ', 'english' : 'ae'}, 
            {'key' : 'ㅡ', 'english' : 'eu'}, 
            {'key' : 'ㅢ', 'english' : 'ui'}, 
            {'key' : 'ㅚ', 'english' : 'oe'}, 
            {'key' : 'ㅟ', 'english' : 'wi'}, 

        ]
        self.nowIndex = 0

    def __init__(self):
        super().__init__()
        self.initData()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Finger Spelling Collector')
        self.move(300, 300)
        self.resize(500, 600)
        self.setStyleSheet("background-color:#fff")

        self.rootVBoxLayout = QVBoxLayout()
        self.setLayout(self.rootVBoxLayout)

        self.labelVBoxLayout = QVBoxLayout()
        self.status = 0
        self.statusLabel = QLabel("Enter 키를 눌러 수집을 시작하세요")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setStyleSheet("color:#000;font-size:16px;text-align:center")
        self.rootVBoxLayout.addWidget(self.statusLabel)

        self.image_label = QLabel(self)
        self.image_label.resize(500, 600)
        self.rootVBoxLayout.addWidget(self.image_label)
        self.instructionImage = QLabel(self)
        self.instructionImage.resize(500, 600)
        self.instructionImagePixMap = QtGui.QPixmap("./assets/consonant.jpeg")
        self.instructionImage.setPixmap(self.instructionImagePixMap.scaled(500, 600, Qt.KeepAspectRatio))
        self.rootVBoxLayout.addWidget(self.instructionImage)

        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

        self.show()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(500, 600, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

        elif e.key() == 16777220:
            if self.status == 0:
                try:
                    if not os.path.exists("./outputs"):
                        os.mkdir("./outputs")
                    
                    self.nowDirectory = "./outputs/" + str(int(time.time()))
                    os.mkdir(self.nowDirectory)
                except OSError:
                    pass

                self.status = 1
                
                self.statusLabel.setText("Enter를 눌러 '" + self.collectionTarget[self.nowIndex]["key"] + "' 지문자를 촬영하세요("+str(self.nowIndex+1)+"/"+str(len(self.collectionTarget))+")")

            elif self.status == 1:
                if self.nowIndex < len(self.collectionTarget):
                    try:
                        os.mkdir(self.nowDirectory + "/" + self.collectionTarget[self.nowIndex]["english"])
                        
                    except OSError:
                        pass

                    self.recordStartTime = time.time()
                    self.prevCaptureTime = time.time()
                    self.nowTime = time.time()
                    
                    self.nowPictureCount = 1
                    cap = cv2.VideoCapture(0)
                    while(self.nowTime - self.recordStartTime <= 1):
                        self.currentTime = time.time() - self.prevCaptureTime
                        if(self.currentTime > 1. / 60):
                            ret, cv_img = cap.read()
                            if ret:
                                cv2.imwrite(self.nowDirectory + "/" + self.collectionTarget[self.nowIndex]["english"] + "/" + str(self.nowPictureCount) + ".png", cv_img)
                                self.nowPictureCount = self.nowPictureCount + 1
                                self.prevCaptureTime = time.time()

                        self.nowTime = time.time()

                    self.nowIndex = self.nowIndex + 1
                    if self.nowIndex == len(self.collectionTarget):
                        self.status = 0
                        self.statusLabel.setText("수집이 종료되었습니다. 추가적인 수집을 원하시는 경우 Enter를 눌러주세요")
                        self.instructionImagePixMap = QtGui.QPixmap("./assets/consonant.jpeg")
                        self.instructionImage.setPixmap(self.instructionImagePixMap.scaled(500, 600, Qt.KeepAspectRatio))
                    else :
                        self.statusLabel.setText("Enter를 눌러 '" + self.collectionTarget[self.nowIndex]["key"] + "' 지문자를 촬영하세요("+str(self.nowIndex+1)+"/"+str(len(self.collectionTarget))+")")

                    if self.nowIndex == 13:
                        self.instructionImagePixMap = QPixmap("./assets/vowel.jpeg")
                        self.instructionImage.setPixmap(self.instructionImagePixMap.scaled(500, 600, Qt.KeepAspectRatio))

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = FingerSpellingCollector()
   sys.exit(app.exec_())