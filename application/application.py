from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QGridLayout
from application.view import game_view

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500


def launch():
    import sys
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('qyz_surakarta')
        self.resize(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.__init_view()
        center_x, center_y = self.__get_screen_center()
        self.move(center_x, center_y)

    def __init_view(self):
        layout = QGridLayout()
        view = game_view.GameView()
        layout.addWidget(view)
        self.setLayout(layout)

    @staticmethod
    def __get_screen_center():
        screen = QDesktopWidget().screenGeometry()
        return (screen.width() - SCREEN_WIDTH) / 2, (screen.height() - SCREEN_HEIGHT) / 2
