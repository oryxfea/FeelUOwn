# -*- coding:utf8 -*-

import platform
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from interfaces import ControllerApi


class LyricWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._text_label = QLabel()
        self._container = QWidget(self)
        self._container_layout = QVBoxLayout(self._container)

        self._exit_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self._exit_shortcut.activated.connect(self.close)

        self._layout = QVBoxLayout(self)
        self.__drag_pos = (0, 0)
        self._init_attr()

        self.__lyrics = []
        self.__translate_lyric = []
        self.__time_sequence = []

        self.__init_layout()
        self.close()

    def paintEvent(self, event: QPaintEvent):
        """
        self is derived from QWidget, Stylesheets don't work unless \
        paintEvent is reimplemented.y
        at the same time, if self is derived from QFrame, this isn't needed.
        """
        option = QStyleOption()
        option.initFrom(self)
        painter = QPainter(self)
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        style = self.style()
        style.drawPrimitive(QStyle.PE_Widget, option, painter, self)

    def set_text(self, p_str):
        self._text_label.setText(p_str)

    def set_alignment(self, align):
        self._text_label.setAlignment(align)

    def _init_attr(self):
        height = 60
        width = 800
        self.setMouseTracking(False)
        self.setObjectName('lyric_label_container')
        self._text_label.setObjectName("lyric_label")
        self._text_label.setText("音乐感知生活")
        self.set_alignment(Qt.AlignCenter)

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._container_layout.setSpacing(0)

        self._container.setLayout(self._container_layout)
        self.setLayout(self._layout)

        if platform.system() == "Linux":
            self.setWindowFlags(Qt.X11BypassWindowManagerHint)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)

        self.resize(width, height)
        self.move((QApplication.desktop().width() - width)/2, 40)

    def reset_lyric(self):
        self.__lyrics = []
        self.__translate_lyric = []
        self.__time_sequence = []

    def set_lyric(self, lyric_model):
        self.hide()
        self.show()
        self.__time_sequence = lyric_model['time_sequence']
        self.__lyrics = lyric_model['lyric']
        self.__translate_lyric = lyric_model['translate_lyric']

    def has_lyric(self):
        if self.__lyrics:
            return True
        return False

    def sync_lyric(self, ms):
        if self.has_lyric():
            for i, each in enumerate(self.__time_sequence):
                if ms + 400 >= each:
                    lyric = self.__lyrics[i][:-1]
                    # 翻译歌词比原歌词短
                    if self.__translate_lyric and len(self.__translate_lyric) > i:
                        tlyric = self.__translate_lyric[i][:-1]
                        lyric += "\n" + tlyric
                    self.set_text(lyric)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__drag_pos = event.globalPos() - self.pos()
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.__drag_pos)
            event.accept()
        if event.buttons() == Qt.RightButton:
            event.ignore()

    def __init_layout(self):
        self._container_layout.addWidget(self._text_label)
        self._layout.addWidget(self._container)

    def show_lyric_while_visible(self, ms):
        """给controller调用的函数"""
        if self.isVisible():
            if self.has_lyric():
                self.sync_lyric(ms)
            else:
                lyric_model = ControllerApi.api.get_lyric_detail(ControllerApi.state['current_mid'])
                if not ControllerApi.api.is_response_ok(lyric_model):
                    return

                if lyric_model:
                    self.set_lyric(lyric_model)
                    self.sync_lyric(ms)
                else:
                    self.setText(u'歌曲没有歌词')
