import sys
import os
import random
from PyQt5.QtGui import QIcon, QMovie, QCursor
from PyQt5.QtWidgets import QWidget, QApplication, QSystemTrayIcon, QMenu, QAction, QLabel, QDesktopWidget
from PyQt5.QtCore import Qt, QSize

class DesktopPet(QWidget):
    def __init__(self, parent=None, **kwargs):
        super(DesktopPet, self).__init__(parent)
        self.init()
        self.initPall()
        self.initPetImage()
    
    def init(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()
        
    def initPall(self):
        icons = os.path.join('Image/MenuIcon.jpg')
        quit_action = QAction('退出', self, triggered=self.quit)
        showing = QAction(u'显示', self, triggered=self.showup)
        hideup = QAction(u'隐藏', self, triggered=self.hideup)
        self.tray_icon_menu = QMenu(self)
        self.tray_icon_menu.addAction(quit_action)
        self.tray_icon_menu.addAction(showing)
        self.tray_icon_menu.addAction(hideup)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(icons))
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        self.tray_icon.show()
        
    def initPetImage(self):
        self.image = QLabel(self)
        self.movie = QMovie("GIF/normal.gif")
        self.movie.setScaledSize(QSize(200, 200))
        self.image.setMovie(self.movie)
        self.movie.start()
        self.resize(200, 200)
        self.randomPosition()
        self.show()
        self.pet1 = []
        for filename in os.listdir("GIF"):
            self.pet1.append(os.path.join("GIF", filename))
            
    def showMenu(self, pos):
        menu = QMenu()
        menu.addAction("贴贴", self.stick)
        menu.addAction("拍一拍", self.call)
        menu.addAction("锻炼", self.exercise)
        menu.exec_(self.mapToGlobal(pos))
        
    def stick(self):
        self.movie = QMovie("GIF/stick.gif")
        self.movie.setScaledSize(QSize(200, 200))
        self.image.setMovie(self.movie)
        self.movie.start()
        
    def call(self):
        self.movie = QMovie("GIF/call.gif")
        self.movie.setScaledSize(QSize(200, 200))
        self.image.setMovie(self.movie)
        self.movie.start()
        
    def exercise(self):
        self.movie = QMovie("GIF/exercise.gif")
        self.movie.setScaledSize(QSize(200, 200))
        self.image.setMovie(self.movie)
        self.movie.start()

    def randomPosition(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        pet_geometry = self.geometry()
        width = int((screen_geometry.width() - pet_geometry.width()) * random.random())
        height  = int((screen_geometry.height() - pet_geometry.height()) * random.random())
        self.move(width, height)
        
    def mousePressEvent(self, event):
        self.condition = 1
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            self.setCursor(QCursor(Qt.OpenHandCursor))
        elif event.button() == Qt.RightButton:
            self.showMenu(event.globalPos())
        event.accept()
 
    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
        event.accept()
 
    def mouseReleaseEvent(self, event):
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))
 
    def enterEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)
        
    def quit(self):
        self.close()
        sys.exit()
        
    def showup(self):
        self.setWindowOpacity(1)
        
    def hideup(self):
        self.setWindowOpacity(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec_())  