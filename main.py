import sys
import os
import random
import datetime
from PyQt5.QtGui import QIcon, QMovie, QCursor, QPixmap
from PyQt5.QtWidgets import (QWidget, QApplication, QSystemTrayIcon,
                             QMenu, QAction, QLabel, QDesktopWidget,
                             QProgressBar, QVBoxLayout, QHBoxLayout,
                             QDialog)
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint
from PyQt5.QtWidgets import QTextEdit, QLineEdit, QPushButton

from chat_with_llm import OllamaChat


# ... existing code ...
class ChatDialog(QDialog):
    """
    和小白聊天对话框（粉色主题）
    """
    def __init__(self, parent=None):
        super(ChatDialog, self).__init__(parent)
        self.chat_agent = OllamaChat()
        self.setWindowTitle("小白宝宝")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.resize(320, 420)

        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 聊天记录区
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 230);
                border: 2px solid #FF69B4;
                border-radius: 10px;
                font-size: 14px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.chat_history)

        # 输入区域
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #FF69B4;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        self.send_button = QPushButton("发送")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #FF69B4;
                color: white;
                border-radius: 10px;
                padding: 6px 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FF85C1;
            }
            QPushButton:pressed {
                background-color: #FF4DA6;
            }
        """)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        self.setLayout(layout)

        # 绑定事件
        self.send_button.clicked.connect(self.sendMessage)
        self.input_field.returnPressed.connect(self.sendMessage)

        # --- 这里是新增的欢迎语 ---
        welcome_message = "汪汪~ 我是小白，很高兴见到你！"
        self.chat_history.append(f"<b><span style='color:#FF69B4'>小白：</span></b> {welcome_message}")
        # 将欢迎语作为聊天记录
        self.chat_message = welcome_message
        # ------------------------

    def sendMessage(self):
        user_text = self.input_field.text().strip()
        if not user_text:
            return
        # 显示用户输入（蓝色字体）
        self.chat_history.append(f"<b><span style='color:#1E90FF'>你：</span></b> {user_text}")
        self.input_field.clear()

        # 将用户输入传入语言模型和小白进行交互
        ## 先用ollama吧
        reply = self.chat_agent.chat(user_text)

        # 小白回复（粉色字体）
        self.chat_history.append(f"<b><span style='color:#FF69B4'>小白：</span></b> {reply}")
        # 将回复作为聊天记录
        self.chat_message = reply


class ClockDialog(QDialog):
    """
    时钟对话框类 - 用于显示整点报时信息
    """

    def __init__(self, message, parent=None):
        super(ClockDialog, self).__init__(parent)
        # 设置窗口属性：无边框、工具窗口、置顶显示、无阴影
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)
        # 设置窗口背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout()
        # 创建显示消息的标签
        self.message_label = QLabel(message)
        # 设置标签样式：半透明背景、粉色边框、圆角、内边距、字体大小等
        self.message_label.setStyleSheet("""
            background-color: rgba(255, 255, 255, 225);
            border: 2px solid #FF69B4;
            border-radius: 10px;
            padding: 10px;
            color: #333;
            font-size: 14px;
        """)
        layout.addWidget(self.message_label)
        self.setLayout(layout)
        # 创建定时器，9.5秒后自动关闭对话框
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close)
        self.timer.start(9500)


class DesktopPet(QWidget):
    """
    桌面宠物主类 - 控制整个宠物应用的行为和界面
    """

    def __init__(self, parent=None, **kwargs):
        super(DesktopPet, self).__init__(parent)
        # 初始化窗口属性
        self.init()
        # 初始化系统托盘
        self.initPall()
        # 创建动作定时器，用于控制动画播放时间
        self.action_timer = QTimer(self)
        self.action_timer.setSingleShot(True)
        self.action_timer.timeout.connect(self.checkInitialGif)
        # 创建状态更新定时器
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.statusTimer)
        # 累计幸福值和能量值变化量
        self.happiness_accumulated = 0
        self.energy_accumulated = 0
        # 创建工作状态定时器
        self.working_timer = QTimer(self)
        self.working_timer.timeout.connect(self.updateWorking)
        # 创建无聊状态定时器
        self.boring_timer = QTimer(self)
        self.boring_timer.setSingleShot(True)
        self.boring_timer.timeout.connect(self.setBoring)
        self.is_boring = False
        # 重置无聊定时器
        self.resetBoringTimer()
        # 复活定时器 - 宠物死亡后30分钟复活
        self.resurrect_timer = QTimer(self)
        self.resurrect_timer.setSingleShot(True)
        self.resurrect_timer.timeout.connect(self.resurrectPet)
        self.is_dead = False
        # 整点报时定时器 - 每秒检查一次时间
        self.hour_timer = QTimer(self)
        self.hour_timer.timeout.connect(self.hourAlert)
        self.hour_timer.start(1000)
        self.last_hour = -1
        # 初始化宠物图像
        self.initPetImage()

    def init(self):
        """
        初始化窗口基本属性
        """
        # 设置窗口标志：无边框、置顶、工具窗口、无阴影
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.NoDropShadowWindowHint)
        # 设置背景自动填充为False
        self.setAutoFillBackground(False)
        # 设置窗口背景透明
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 重新绘制窗口
        self.repaint()

    def initPall(self):
        """
        初始化系统托盘图标和菜单
        """
        icons = os.path.join('Image/MenuIcon.jpg')
        # 创建托盘菜单项
        self.quit_action = QAction(u'退出', self, triggered=self.quit)  # 退出应用
        self.showing = QAction(u'显示', self, triggered=self.showup)  # 显示宠物
        self.hideup = QAction(u'隐藏', self, triggered=self.hide)  # 隐藏宠物
        self.hidestats = QAction(u'显示/隐藏状态栏', self, triggered=self.hideStatsBar)  # 显示/隐藏状态栏
        # 创建托盘菜单并添加动作项
        self.tray_icon_menu = QMenu(self)
        self.tray_icon_menu.addAction(self.quit_action)
        self.tray_icon_menu.addAction(self.showing)
        self.tray_icon_menu.addAction(self.hideup)
        self.tray_icon_menu.addAction(self.hidestats)
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(icons))
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        self.tray_icon.show()

    def initPetImage(self):
        """
        初始化宠物图像和界面布局
        """
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        # 随机选择普通状态动画
        self.normal_form = random.random()

        # 初始化状态栏可见性
        self.stats_visible = True
        # 创建幸福值状态栏布局
        self.happiness_layout = QHBoxLayout()
        self.happiness_layout.setContentsMargins(0, 0, 0, 0)
        self.happiness_layout.setSpacing(0)
        self.happiness_icon = QLabel()
        self.happiness_icon.setContentsMargins(0, 0, 0, 0)
        # 加载幸福值图标并缩放
        self.happiness_icon_pixmap = QPixmap("Image/Happiness.svg")
        self.happiness_icon_pixmap = self.happiness_icon_pixmap.scaled(QSize(20, 20), Qt.KeepAspectRatio,
                                                                       Qt.SmoothTransformation)
        self.happiness_icon.setPixmap(self.happiness_icon_pixmap)
        self.happiness_layout.addWidget(self.happiness_icon, alignment=Qt.AlignCenter)
        # 创建幸福值进度条
        self.happiness_bar = QProgressBar()
        self.happiness_bar.setRange(0, 100)  # 设置范围0-100
        self.happiness_bar.setValue(80)  # 初始值80
        self.happiness_bar.setFixedHeight(12)  # 固定高度
        self.happiness_bar.setFixedWidth(150)  # 固定宽度
        # 设置进度条样式
        self.happiness_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #FF69B4;
            }
        """)
        self.happiness_layout.addWidget(self.happiness_bar, alignment=Qt.AlignCenter)

        # 创建能量值状态栏布局
        self.energy_layout = QHBoxLayout()
        self.energy_layout.setContentsMargins(0, 0, 0, 0)
        self.energy_layout.setSpacing(0)
        self.energy_label = QLabel()
        self.energy_label.setContentsMargins(0, 0, 0, 0)
        # 加载能量值图标并缩放
        self.energy_icon_pixmap = QPixmap("Image/Energy.svg")
        self.energy_icon_pixmap = self.energy_icon_pixmap.scaled(QSize(20, 20), Qt.KeepAspectRatio,
                                                                 Qt.SmoothTransformation)
        self.energy_label.setPixmap(self.energy_icon_pixmap)
        self.energy_layout.addWidget(self.energy_label, alignment=Qt.AlignCenter)
        # 创建能量值进度条
        self.energy_bar = QProgressBar()
        self.energy_bar.setRange(0, 100)  # 设置范围0-100
        self.energy_bar.setValue(80)  # 初始值80
        self.energy_bar.setFixedHeight(12)  # 固定高度
        self.energy_bar.setFixedWidth(150)  # 固定宽度
        # 设置进度条样式
        self.energy_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #1E90FF;
            }
        """)
        self.energy_layout.addWidget(self.energy_bar, alignment=Qt.AlignCenter)

        # 创建显示动画的标签
        self.image = QLabel(self)
        self.image.setContentsMargins(0, 0, 0, 0)
        # 检查并设置初始GIF动画
        self.checkInitialGif()

        # 将控件添加到主布局中
        self.main_layout.addWidget(self.image)
        self.main_layout.addLayout(self.happiness_layout)
        self.main_layout.addLayout(self.energy_layout)

        # 设置窗口大小并随机定位
        self.resize(200, 240)
        self.randomPosition()
        self.show()
        # 加载所有宠物动画文件
        self.pet1 = []
        for filename in os.listdir("GIF"):
            self.pet1.append(os.path.join("GIF", filename))

    def showMenu(self):
        """
        显示右键菜单
        """
        menu = QMenu()
        # 添加菜单项
        menu.addAction(u"贴贴", self.stick)  # 贴贴互动
        menu.addAction(u"拍一拍", self.call)  # 拍一拍互动
        menu.addAction(u"锻炼", self.exercise)  # 锻炼
        menu.addAction(u"充电", self.charge)  # 充电
        menu.addAction(u"投喂小白", self.cake)  # 投喂
        menu.addAction(u"吧唧", self.baji)  # 吧唧（亲亲）
        menu.addAction(u"随机出现", self.appear)  # 随机出现
        menu.addAction(u"遛小鸡毛", self.walkDog)  # 遛狗
        menu.addAction(u"和小白聊天", self.chatDog) # 和小白聊天
        # 在宠物右侧显示菜单
        right_pos = self.mapToGlobal(self.rect().topRight())
        menu.exec_(right_pos)

    def chatDog(self):
        """
        和小白聊天 - 弹出聊天窗口
        """
        if self.is_dead:
            return
        self.resetBoringTimer()
        self.working_timer.stop()

        self.chat_dialog = ChatDialog(parent=self)
        self.chat_dialog.show()

        # 要根据对话的内容的心情改变GIF
        ## 获取对话内容
        message = self.chat_dialog.chat_message

        ## 根据对话内容改变GIF bert 情感分析



    def stick(self):
        """
        贴贴互动 - 增加幸福值，减少能量值
        """
        if self.is_dead:
            return
        self.resetBoringTimer()
        self.working_timer.stop()
        self.changeGif("GIF/stick.gif")
        # 设置动作持续时间10分钟
        self.action_timer.start(10 * 60 * 1000)
        # 更新状态：增加15幸福值，减少5能量值，持续10分钟
        self.updateStatus(15, -5, 10 * 60 * 1000)

    def call(self):
        """
        拍一拍互动 - 短暂互动
        """
        if self.is_dead:
            return
        self.resetBoringTimer()
        self.working_timer.stop()
        self.changeGif("GIF/call.gif")
        # 设置动作持续时间2秒
        self.action_timer.start(2000)

    def exercise(self):
        """
        锻炼 - 增加幸福值，大幅减少能量值
        """
        if self.is_dead:
            return
        self.resetBoringTimer()
        self.working_timer.stop()
        self.changeGif("GIF/exercise.gif")
        # 设置动作持续时间10分钟
        self.action_timer.start(10 * 60 * 1000)
        # 更新状态：增加5幸福值，减少15能量值，持续10分钟
        self.updateStatus(5, -15, 10 * 60 * 1000)

    def charge(self):
        """
        充电 - 大幅增加幸福值和能量值
        """
        if self.is_dead:
            return
        self.resetBoringTimer()
        self.working_timer.stop()
        self.changeGif("GIF/charge.gif")
        # 设置动作持续时间1小时
        self.action_timer.start(60 * 60 * 1000)
        # 更新状态：增加30幸福值和能量值，持续30分钟
        self.updateStatus(30, 30, 30 * 60 * 1000)

    def cake(self):
        """
        投喂 - 根据能量值状态显示不同动画
        """
        if self.is_dead:
            return
        self.resetBoringTimer()
        self.working_timer.stop()
        # 如果能量值高于80，显示吃撑了的动画
        if self.energy_bar.value() >= 80:
            self.changeGif("GIF/full.gif")
            self.action_timer.start(5 * 1000)  # 持续5秒
        else:
            # 否则显示正常进食动画
            self.changeGif("GIF/cake.gif")
            self.action_timer.start(5 * 60 * 1000)  # 持续5分钟
            # 更新状态：增加10幸福值，增加5能量值，持续5分钟
            self.updateStatus(10, 5, 5 * 60 * 1000)

    def baji(self):
        """
        吧唧（亲亲） - 增加幸福值
        """
        if self.is_dead:
            return
        self.resetBoringTimer()
        self.working_timer.stop()
        self.changeGif("GIF/baji.gif")
        # 设置动作持续时间5分钟
        self.action_timer.start(5 * 60 * 1000)
        # 更新状态：增加10幸福值，能量值不变，持续5分钟
        self.updateStatus(10, 0, 5 * 60 * 1000)

    def appear(self):
        """
        随机出现 - 在屏幕随机位置显示宠物
        """
        if self.is_dead:
            return
        self.resetBoringTimer()
        self.working_timer.stop()
        self.changeGif("GIF/appear.gif")
        self.action_timer.start(3500)  # 持续3.5秒
        self.randomPosition()  # 随机改变位置

    def walkDog(self):
        """
        遛狗 - 中等增加幸福值，减少能量值
        """
        if self.is_dead:
            return
        self.resetBoringTimer()
        self.working_timer.stop()
        self.changeGif("GIF/walkdog.gif")
        # 设置动作持续时间10分钟
        self.action_timer.start(10 * 60 * 1000)
        # 更新状态：增加15幸福值，减少10能量值，持续10分钟
        self.updateStatus(15, -10, 10 * 60 * 1000)

    def checkInitialGif(self):
        """
        检查并设置初始GIF动画 - 根据时间、工作日和状态值决定显示哪个动画
        """
        current_time = datetime.datetime.now()
        current_hour = current_time.hour
        weekday = current_time.weekday()
        # 判断是否为工作时间（周一到周五，10点到18点）
        self.is_working_time = (0 <= weekday <= 4) and (10 <= current_hour < 18)
        happiness = self.happiness_bar.value()
        energy = self.energy_bar.value()

        # 根据幸福值和能量值状态选择动画
        if happiness == 0 and energy == 0:
            # 幸福值和能量值都为0，宠物死亡
            self.petDied()
        elif happiness < 20 and energy < 20:
            # 幸福值和能量值都低于20，显示愤怒动画
            if self.is_working_time:
                self.working_timer.stop()
            self.working_timer.start(60 * 1000)  # 每分钟更新状态
            return self.changeGif("GIF/angry.gif")
        elif happiness < 20:
            # 幸福值低于20，显示哭泣动画2
            if self.is_working_time:
                self.working_timer.stop()
            self.working_timer.start(2 * 60 * 1000)  # 每2分钟更新状态
            return self.changeGif("GIF/crying2.gif")
        elif energy < 20:
            # 能量值低于20，显示哭泣动画
            if self.is_working_time:
                self.working_timer.stop()
            self.working_timer.start(2 * 10 * 1000)  # 每20秒更新状态
            return self.changeGif("GIF/crying.gif")
        elif energy >= 20 and energy < 40:
            # 能量值在20-40之间，显示饥饿动画
            return self.changeGif("GIF/hungry.gif")

        # 根据是否工作时间选择动画
        if self.is_working_time:
            self.working_timer.start(3 * 60 * 1000)  # 每3分钟更新状态
            return self.changeGif("GIF/working2.gif")
        else:
            self.working_timer.stop()
            # 非工作时间随机显示普通状态动画
            if self.normal_form < 0.5:
                return self.changeGif("GIF/normal.gif")
            else:
                return self.changeGif("GIF/normal2.gif")

    def updateWorking(self):
        """
        更新工作状态 - 每隔一段时间自动减少幸福值和能量值
        """
        self.updateHappiness(-1)  # 减少1点幸福值
        self.updateEnergy(-1)  # 减少1点能量值
        # 如果幸福值或能量值低于20，检查并更新动画
        if self.happiness_bar.value() <= 20 or self.energy_bar.value() <= 20:
            self.checkInitialGif()

    def updateStatus(self, happinesschange, energychange, duration):
        """
        更新状态值 - 在指定持续时间内逐渐改变幸福值和能量值
        :param happinesschange: 幸福值变化量
        :param energychange: 能量值变化量
        :param duration: 持续时间（毫秒）
        """
        self.total_happiness_change = happinesschange
        self.total_energy_change = energychange
        interval = 100  # 更新间隔100毫秒
        self.remaining = duration / interval  # 计算更新次数
        # 计算每次更新的变化量
        self.happiness_change_step = happinesschange / self.remaining
        self.energy_change_step = energychange / self.remaining
        self.status_timer.start(interval)  # 启动状态更新定时器

    def statusTimer(self):
        """
        状态定时器处理函数 - 逐步更新幸福值和能量值
        """
        if self.remaining <= 0:
            self.status_timer.stop()
            return
        # 累计变化量
        self.happiness_accumulated += self.happiness_change_step
        self.energy_accumulated += self.energy_change_step
        # 如果累计变化量绝对值大于等于1，则更新状态值
        if self.happiness_accumulated >= 1 or self.happiness_accumulated <= -1:
            self.updateHappiness(int(self.happiness_accumulated))
            self.happiness_accumulated = 0
        if self.energy_accumulated >= 1 or self.energy_accumulated <= -1:
            self.updateEnergy(int(self.energy_accumulated))
            self.energy_accumulated = 0
        self.remaining -= 1  # 剩余更新次数减1

    def setBoring(self):
        """
        设置无聊状态 - 非工作时间长时间无操作时触发
        """
        if not self.is_boring and not self.is_working_time:
            self.is_boring = True
            self.changeGif("GIF/boring.gif")
            self.updateHappiness(-5)  # 减少5点幸福值

    def resetBoringTimer(self):
        """
        重置无聊定时器 - 用户操作时调用，重置无聊状态
        """
        if self.is_boring:
            self.is_boring = False
            self.checkInitialGif()
        self.boring_timer.stop()
        # 设置1小时后触发无聊状态
        self.boring_timer.start(60 * 60 * 1000)

    def petDied(self):
        """
        宠物死亡处理 - 幸福值和能量值都为0时触发
        """
        if self.is_dead:
            return
        self.is_dead = True
        # 停止所有定时器
        self.working_timer.stop()
        self.boring_timer.stop()
        self.action_timer.stop()
        self.status_timer.stop()
        # 禁用相关菜单项
        self.showing.setEnabled(False)
        self.hidestats.setEnabled(False)
        self.hideup.setEnabled(False)
        self.hide()  # 隐藏宠物
        # 30分钟后复活
        self.resurrect_timer.start(30 * 60 * 1000)

    def resurrectPet(self):
        """
        复活宠物 - 30分钟后自动复活
        """
        self.is_dead = False
        # 恢复初始状态值
        self.happiness_bar.setValue(30)
        self.energy_bar.setValue(30)
        # 启用相关菜单项
        self.showing.setEnabled(True)
        self.hidestats.setEnabled(True)
        self.hideup.setEnabled(True)
        self.showup()  # 显示宠物
        self.resetBoringTimer()  # 重置无聊定时器
        self.checkInitialGif()  # 检查并设置初始动画

    def hourAlert(self):
        """
        整点报时 - 每小时整点显示时间提醒（不受 action_timer 阻挡）
        """
        if self.is_dead:
            return
        current_time = datetime.datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        # 如果是整点且不是已经提醒过的小时
        if current_minute == 0 and current_hour != self.last_hour:
            self.last_hour = current_hour
            # 弹出报时对话框，但不停止宠物动作
            self.clock_dialog = ClockDialog(
                message=f"现在是北京时间 {current_hour} 点整！",
                parent=self
            )
            self.clock_dialog.move(self.updateDialogPosition())
            self.clock_dialog.show()

    def randomPosition(self):
        """
        随机定位 - 将宠物随机放置在屏幕上的某个位置
        """
        screen_geometry = QDesktopWidget().screenGeometry()
        pet_geometry = self.geometry()
        # 计算随机位置
        width = int((screen_geometry.width() - pet_geometry.width()) * random.random())
        height = int((screen_geometry.height() - pet_geometry.height()) * random.random())
        self.move(width, height)

    def changeGif(self, path):
        """
        更改GIF动画
        :param path: GIF文件路径
        """
        self.movie = QMovie(path)
        self.movie.setScaledSize(QSize(200, 200))  # 缩放GIF大小
        self.image.setMovie(self.movie)
        self.movie.start()

    def mousePressEvent(self, event):
        """
        鼠标按下事件处理
        """
        self.condition = 1
        if event.button() == Qt.LeftButton:
            # 左键按下，准备拖动
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 设置鼠标样式为张开的手
        elif event.button() == Qt.RightButton:
            # 右键按下，显示菜单
            self.showMenu()
        event.accept()

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件处理 - 实现拖动功能
        """
        if Qt.LeftButton and self.is_follow_mouse:
            # 移动宠物位置
            self.move(event.globalPos() - self.mouse_drag_pos)
            # 如果时钟对话框存在且可见，同步移动对话框
            if hasattr(self, 'clock_dialog') and self.clock_dialog.isVisible():
                self.clock_dialog.move(self.updateDialogPosition())
        event.accept()

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件处理
        """
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))  # 恢复鼠标为箭头样式

    def enterEvent(self, event):
        """
        鼠标进入事件处理 - 改变鼠标样式
        """
        self.setCursor(Qt.ClosedHandCursor)  # 设置鼠标样式为握拳的手

    def updateHappiness(self, value):
        """
        更新幸福值
        :param value: 幸福值变化量
        """
        current_value = self.happiness_bar.value()
        # 限制幸福值在0-100之间
        new_value = max(0, min(100, current_value + value))
        self.happiness_bar.setValue(new_value)

    def updateEnergy(self, value):
        """
        更新能量值
        :param value: 能量值变化量
        """
        current_value = self.energy_bar.value()
        # 限制能量值在0-100之间
        new_value = max(0, min(100, current_value + value))
        self.energy_bar.setValue(new_value)

    def hideStatsBar(self):
        """
        显示/隐藏状态栏
        """
        if self.is_dead:
            return
        self.stats_visible = not self.stats_visible
        # 切换状态栏可见性
        self.happiness_icon.setVisible(self.stats_visible)
        self.happiness_bar.setVisible(self.stats_visible)
        self.energy_label.setVisible(self.stats_visible)
        self.energy_bar.setVisible(self.stats_visible)

    def updateDialogPosition(self):
        """
        更新对话框位置 - 使对话框显示在宠物上方
        """
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        pet_pos = self.pos()
        pet_width = self.width()
        pet_height = self.height()
        if hasattr(self, 'clock_dialog'):
            dialog_width = self.clock_dialog.width()
            dialog_height = self.clock_dialog.height()
        # 计算对话框位置
        x = pet_pos.x() + pet_width // 2
        y = pet_pos.y()
        # 防止对话框超出屏幕右边界
        if x + dialog_width > screen_width:
            x = pet_pos.x() - dialog_width // 2
        # 防止对话框超出屏幕上边界
        if y < 0:
            y = 0
        return QPoint(x, y)

    def quit(self):
        """
        退出应用
        """
        self.close()
        sys.exit()

    def showup(self):
        """
        显示宠物
        """
        self.setWindowOpacity(1)

    def hide(self):
        """
        隐藏宠物
        """
        self.setWindowOpacity(0)


# 程序入口点
if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec_())