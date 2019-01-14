from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout
from PyQt5.QtGui import *
import sip
from application.view.target_button import TargetButton
from application.view.chess_button import ChessButton
from abc import ABCMeta, abstractmethod

INTERVAL = 50
LONG_RADIUS = INTERVAL * 4
SHORT_RADIUS = INTERVAL * 2
CHESS_SIZE = 30


class GameView(QWidget):

    def __init__(self, *__args):
        super().__init__(*__args)
        self.click_callback = None
        self.target_click_callback = None
        self.chess_move_callback = None
        self.targets = []
        self.chess_list = []
        self.__init_view()

    def __init_view(self):
        begin_x = INTERVAL * 2
        begin_y = INTERVAL * 2
        for i in range(0, 24):
            btn = ChessButton(self)
            if i < 6:
                btn.setup_view(True)
                btn.setGeometry(begin_x + INTERVAL * i - CHESS_SIZE / 2,
                                begin_y - CHESS_SIZE / 2,
                                CHESS_SIZE,
                                CHESS_SIZE)
            elif i < 12:
                btn.setup_view(True)
                btn.setGeometry(begin_x + INTERVAL * (i - 6) - CHESS_SIZE / 2,
                                begin_y + INTERVAL - CHESS_SIZE / 2,
                                CHESS_SIZE,
                                CHESS_SIZE)
            elif i < 18:
                btn.setup_view(False)
                btn.setGeometry(begin_x + INTERVAL * (i - 12) - CHESS_SIZE / 2,
                                begin_y + INTERVAL * 4 - CHESS_SIZE / 2,
                                CHESS_SIZE,
                                CHESS_SIZE)
            else:
                btn.setup_view(False)
                btn.setGeometry(begin_x + INTERVAL * (i - 18) - CHESS_SIZE / 2,
                                begin_y + INTERVAL * 5 - CHESS_SIZE / 2,
                                CHESS_SIZE,
                                CHESS_SIZE)
            btn.setText(str(i + 1))
            btn.tag = i + 1
            btn.clicked.connect(self.__click_btn)
            self.chess_list.append(btn)

    def show_targets(self, frames):
        self.remove_all_targets()
        for frame in frames:
            btn = TargetButton(self)
            btn.setup_frame(frame)
            btn.clicked.connect(self.__click_target_btn)
            btn.show()
            self.targets.append(btn)

    def remove_all_targets(self):
        for btn in self.targets:
            btn.hide()
            sip.delete(btn)
        self.targets.clear()

    def remove_chess(self, tag):
        for btn in self.chess_list:
            if btn.tag == tag:
                self.chess_list.remove(btn)
                btn.hide()
                sip.delete(btn)
                break

    def move_chess(self, chess_tag, to_frame):
        for chess in self.chess_list:
            if chess_tag == chess.tag:
                chess.move(to_frame[1] - CHESS_SIZE / 2, to_frame[0] - CHESS_SIZE / 2)
                # 移动完棋子要回调修改棋盘数据
                return self.chess_move_callback(to_frame)

    @pyqtSlot()
    def __click_btn(self):
        return self.click_callback(self.sender().tag)

    @pyqtSlot()
    def __click_target_btn(self):
        return self.target_click_callback(self.sender().x, self.sender().y)

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        painter.setPen(QColor(166, 66, 250))
        painter.begin(self)
        # 左上
        painter.drawArc(0, 0, LONG_RADIUS, LONG_RADIUS, 0, 270 * 16)
        painter.drawArc(INTERVAL, INTERVAL, SHORT_RADIUS, SHORT_RADIUS, 0, 270 * 16)

        # 左下
        painter.drawArc(0, INTERVAL * 5, LONG_RADIUS, LONG_RADIUS, 90 * 16, 270 * 16)
        painter.drawArc(INTERVAL, INTERVAL * 6, SHORT_RADIUS, SHORT_RADIUS, 90 * 16, 270 * 16)

        # 右上
        painter.drawArc(INTERVAL * 5, 0, LONG_RADIUS, LONG_RADIUS, -90 * 16, 270 * 16)
        painter.drawArc(INTERVAL * 6, INTERVAL, SHORT_RADIUS, SHORT_RADIUS, -90 * 16, 270 * 16)

        # 右下
        painter.drawArc(INTERVAL * 5, INTERVAL * 5, LONG_RADIUS, LONG_RADIUS, -180 * 16, 270 * 16)
        painter.drawArc(INTERVAL * 6, INTERVAL * 6, SHORT_RADIUS, SHORT_RADIUS, -180 * 16, 270 * 16)

        # 竖线
        painter.drawLine(INTERVAL * 2, INTERVAL * 2, INTERVAL * 2, INTERVAL * 7)
        painter.drawLine(INTERVAL * 3, INTERVAL * 2, INTERVAL * 3, INTERVAL * 7)
        painter.drawLine(INTERVAL * 4, INTERVAL * 2, INTERVAL * 4, INTERVAL * 7)
        painter.drawLine(INTERVAL * 5, INTERVAL * 2, INTERVAL * 5, INTERVAL * 7)
        painter.drawLine(INTERVAL * 6, INTERVAL * 2, INTERVAL * 6, INTERVAL * 7)
        painter.drawLine(INTERVAL * 7, INTERVAL * 2, INTERVAL * 7, INTERVAL * 7)

        # 横线
        painter.drawLine(INTERVAL * 2, INTERVAL * 2, INTERVAL * 7, INTERVAL * 2)
        painter.drawLine(INTERVAL * 2, INTERVAL * 3, INTERVAL * 7, INTERVAL * 3)
        painter.drawLine(INTERVAL * 2, INTERVAL * 4, INTERVAL * 7, INTERVAL * 4)
        painter.drawLine(INTERVAL * 2, INTERVAL * 5, INTERVAL * 7, INTERVAL * 5)
        painter.drawLine(INTERVAL * 2, INTERVAL * 6, INTERVAL * 7, INTERVAL * 6)
        painter.drawLine(INTERVAL * 2, INTERVAL * 7, INTERVAL * 7, INTERVAL * 7)
        painter.drawLine(INTERVAL * 2, INTERVAL * 7, INTERVAL * 7, INTERVAL * 7)

        painter.end()
