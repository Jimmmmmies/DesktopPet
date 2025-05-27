import sys
import os
import random
from PyQt5.QtGui import QIcon, QMovie, QCursor, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QSystemTrayIcon, QMenu, QAction, QLabel, QDesktopWidget
from PyQt5.QtCore import Qt, QSize

class DesktopPet(QWidget):
    def __init__(self, parent=None, **kwargs):
        super(DesktopPet, self).__init__(parent)
        self.init()
        self.initPall()
        self.initPetImage()
    
    def init(self):
        # 窗口初始化设置
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 添加以下属性设置以优化渲染
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.repaint()
        
    def initPall(self):
        # 托盘图标设置
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
        # 初始化图像标签
        self.image = QLabel(self)
        
        # 关键设置：确保QLabel完全透明且无边框
        self.image.setAttribute(Qt.WA_TranslucentBackground, True)
        self.image.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        
        # 加载初始动画
        self.cleanChangeAnimation("GIF/normal.gif")
        
        self.resize(200, 200)
        self.randomPosition()
        self.show()
        
        # 预加载所有GIF文件路径
        self.pet1 = []
        if os.path.exists("GIF"):
            for filename in os.listdir("GIF"):
                if filename.endswith('.gif'):
                    self.pet1.append(os.path.join("GIF", filename))
    
    def cleanChangeAnimation(self, gif_path):
        """安全切换动画，避免轮廓线残留"""
        # 停止并清除当前动画
        if hasattr(self, 'movie'):
            self.movie.stop()
            self.image.clear()
            self.movie.deleteLater()
        
        # 强制重绘清除残留
        self.image.repaint()
        QApplication.processEvents()
        
        # 加载新动画
        self.movie = QMovie(gif_path)
        if not self.movie.isValid():
            print(f"无法加载GIF文件: {gif_path}")
            return
        
        self.movie.setScaledSize(QSize(200, 200))
        
        # 连接帧变化信号，确保每帧都刷新
        self.movie.frameChanged.connect(self.forceRepaint)
        
        self.image.setMovie(self.movie)
        self.movie.start()
    
    def forceRepaint(self):
        """强制重绘窗口"""
        self.image.repaint()
        self.update()
            
    def showMenu(self, pos):
        menu = QMenu()
        menu.addAction("贴贴", lambda: self.cleanChangeAnimation("GIF/stick.gif"))
        menu.addAction("拍一拍", lambda: self.cleanChangeAnimation("GIF/call.gif"))
        menu.addAction("锻炼", lambda: self.cleanChangeAnimation("GIF/exercise.gif"))
        menu.exec_(self.mapToGlobal(pos))
        
    def randomPosition(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        pet_geometry = self.geometry()
        width = int((screen_geometry.width() - pet_geometry.width()) * random.random())
        height = int((screen_geometry.height() - pet_geometry.height()) * random.random())
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
    
    # 确保资源路径正确
    if not os.path.exists("GIF"):
        os.makedirs("GIF")
        print("请将GIF动画文件放入GIF文件夹中")
    
    pet = DesktopPet()
    sys.exit(app.exec_())