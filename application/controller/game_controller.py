from application.view import main_window
from application.view import game_view
from PyQt5.QtWidgets import QGridLayout
from surakarta import game
import copy


class GameController:

    def __init__(self):
        self.window = main_window.MainWindow()
        self.selected_tag = 0
        self.move_list = []
        self.__init_view()
        self.game = game.Game(is_debug=True)
        self.game.reset_board()

    def app_launch(self):
        self.window.show()

    def __init_view(self):
        layout = QGridLayout()
        self.game_view = game_view.GameView()
        layout.addWidget(self.game_view)
        self.window.setLayout(layout)
        self.game_view.click_callback = self.__did_click_btn
        self.game_view.target_click_callback = self.__did_click_target_btn
        self.game_view.chess_move_callback = self.__chess_did_move

    def __did_click_btn(self, tag):
        # 1. 获得点击棋子所有可下棋位置
        array = self.game.get_chess_moves(int(tag))
        if len(array) == 0:
            return
        frames = []
        # 2. 获得可下棋位置的界面坐标
        for info in array:
            frames.append(self.__get_chess_frame(info["to"].x, info["to"].y))
        # 3. 展示目标位置
        self.game_view.show_targets(frames)
        self.selected_tag = int(tag)
        self.move_list = copy.deepcopy(array)

    def __did_click_target_btn(self, x, y):
        # 1. 去除目标视图
        self.game_view.remove_all_targets()
        # 2. 移动棋子
        self.game_view.move_chess(self.selected_tag, self.__get_chess_frame(x, y))

    def __chess_did_move(self, frame):
        for info in self.move_list:
            if info["to"].x == frame[2] and info["to"].y == frame[3]:
                # 数据层面移动棋子
                self.game.do_move(info)
                break
        # 清理使用过的数据
        self.selected_tag = 0
        self.move_list.clear()

    @staticmethod
    def __get_chess_frame(x, y):
        interval = game_view.INTERVAL
        begin_x = interval * 2
        begin_y = interval * 2
        return begin_x + x * interval, begin_y + y * interval, x, y
