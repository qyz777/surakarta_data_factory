from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import *

interval = 25


class GameView(QFrame):

    def __init__(self, *__args):
        super().__init__(*__args)

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        painter.setPen(QColor(166, 66, 250))
        painter.begin(self)
        # 左上
        painter.drawArc(0, 0, 100, 100, 0, 270 * 16)
        painter.drawArc(25, 25, 50, 50, 0, 270 * 16)

        # 左下
        painter.drawArc(0, 125, 100, 100, 90 * 16, 270 * 16)
        painter.drawArc(25, 150, 50, 50, 90 * 16, 270 * 16)

        # 右上
        painter.drawArc(125, 0, 100, 100, -90 * 16, 270 * 16)
        painter.drawArc(150, 25, 50, 50, -90 * 16, 270 * 16)

        # 右下
        painter.drawArc(125, 125, 100, 100, -180 * 16, 270 * 16)
        painter.drawArc(150, 150, 50, 50, -180 * 16, 270 * 16)

        # 竖线
        painter.drawLine(50, 50, 50, 175)
        painter.drawLine(75, 50, 75, 175)
        painter.drawLine(100, 50, 100, 175)
        painter.drawLine(125, 50, 125, 175)
        painter.drawLine(150, 50, 150, 175)
        painter.drawLine(175, 50, 175, 175)

        # 横线
        painter.drawLine(50, 50, 175, 50)
        painter.drawLine(50, 75, 175, 75)
        painter.drawLine(50, 100, 175, 100)
        painter.drawLine(50, 125, 175, 125)
        painter.drawLine(50, 150, 175, 150)
        painter.drawLine(50, 175, 175, 175)
        painter.drawLine(50, 175, 175, 175)

        painter.end()
