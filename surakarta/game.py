from surakarta.play_manager import PlayManager
from surakarta.chess import Chess
import copy
import random


class Game(object):

    def __init__(self, camp: int, is_debug=False, game_info: dict = None):
        self._is_debug = is_debug
        self._board_record_list = []
        self._game_info_list = []
        self._red = 12
        self._blue = 12
        self._board = None
        self._camp = camp
        self._play_manager = PlayManager()
        if game_info is not None:
            self._setup_board(game_info)

    def start_play(self):
        """
        自我随机下棋，用来生成棋盘数据
        :return: 棋盘数据，赢的一方阵营
        """
        self.reset_board()
        self._camp = random.choice([-1, 1])
        self._board_record_list = []
        while True:
            moves = self.get_moves()
            move = random.choice(moves)
            self.do_move(move)
            is_win, winner = self.has_winner()
            if is_win:
                break
        return self._board_record_list, winner

    def reset_board(self):
        """
        重置棋盘
        """
        self._red = 12
        self._blue = 12
        self._board_record_list = []
        self._game_info_list = []
        chess_lists = [[] for i in range(6)]
        k = 1
        for i in range(0, 6):
            for j in range(0, 6):
                chess = Chess()
                chess.x = i
                chess.y = j
                if i < 2:
                    chess.camp = -1
                    chess.tag = k
                if 2 <= i < 4:
                    chess.camp = 0
                if 4 <= i < 6:
                    chess.camp = 1
                    chess.tag = k - 12
                k += 1
                chess_lists[i].append(chess)
        self._board = copy.deepcopy(chess_lists)

    def do_move(self, info: dict):
        """
        下棋
        :param info: 下棋的信息 数据结构必须满足 {'from': chess, 'to': chess}
        """
        tread = info['from']
        can_move = info['to']
        tag = tread.tag
        short_a = self._board[tread.x][tread.y]
        short_camp = short_a.camp
        short_a.tag = 0
        short_a.camp = 0
        self._board[tread.x][tread.y] = short_a

        short_b = self._board[can_move.x][can_move.y]
        if short_b.camp == -1:
            self._red -= 1
        if short_b.camp == 1:
            self._blue -= 1
        short_b.tag = tag
        short_b.camp = short_camp
        self._board[can_move.x][can_move.y] = short_b
        new_board = copy.deepcopy(self._board)
        if self.last_board_info is None:
            record_board = new_board
        else:
            record_board = self.last_board_info["board"]
        # 棋盘记录信息
        self._board_record_list.append({
            "board": self._zip_board(record_board),
            "camp": self._camp,
            "red_num": self._red,
            "blue_num": self._blue,
            "chess_num": self._red + self._blue,
            "from_x": tread.x,
            "from_y": tread.y,
            "to_x": can_move.x,
            "to_y": can_move.y
        })
        # 棋盘信息
        self._game_info_list.append({
            "board": new_board,
            "camp": self._camp,
            "red_num": self._red,
            "blue_num": self._blue
        })
        # 修改阵营
        self._camp = -self._camp
        if self._is_debug:
            self.debug_print()

    def cancel_move(self):
        """
        撤回上一步
        """
        if len(self._game_info_list) < 0:
            return
        elif len(self._game_info_list) == 1:
            self.reset_board()
            return
        self._game_info_list.pop()
        last_game_info = self._game_info_list[-1]
        self._board = last_game_info["board"]
        self._camp = last_game_info["camp"]
        self._red = last_game_info["red_num"]
        self._blue = last_game_info["blue_num"]
        if self._is_debug:
            self.debug_print()

    def has_winner(self) -> (bool, int):
        """
        return 是否胜利 camp
        :return: 是否结束，胜利阵营
        """
        if self._red <= 0:
            return True, 1
        if self._blue <= 0:
            return True, -1
        return False, 0

    def get_chess_moves(self, tag: int) -> [dict]:
        """
        获得tag所对应的棋子所有下棋位置
        :param tag: 棋子的tag
        :return: 下棋位置，是一个字典构成的数组
        """
        chess = None
        for i in range(0, 6):
            for j in range(0, 6):
                if self._board[i][j].tag == tag:
                    chess = self._board[i][j]
        return self._play_manager.get_game_moves(chess, self._board)

    def get_moves(self) -> [dict]:
        """
        获取所有可以下棋的位置
        :return: 所有可以下棋的位置，是一个字典构成的数组
        """
        return self._play_manager.get_moves(self._camp, self._board)

    @property
    def chess_num(self):
        """
        所有棋子的数量
        """
        return self._red + self._blue

    @property
    def chess_board(self):
        """
        棋盘数据结构
        """
        return self._board

    @property
    def last_board_info(self) -> dict:
        """
        上一个棋盘的数据结构
        {
            "board": 棋盘数据结构(元素是Chess),
            "camp": 阵营,
            "red_num": 红方棋子数量,
            "blue_num": 蓝方棋子数量
        }
        """
        if len(self._game_info_list) == 0:
            return None
        return self._game_info_list[-1]

    # 根据传参信息初始化棋盘
    def _setup_board(self, info: dict):
        self._board = info["board"]
        self._red = info["red_num"]
        self._blue = info["blue_num"]

    @staticmethod
    def _zip_board(board: [[Chess]]) -> str:
        zip_list = []
        for i in range(0, 6):
            for j in range(0, 6):
                zip_list.append(str(board[i][j].camp))
        return ",".join(zip_list)

    @staticmethod
    def _unzip_board(board: str) -> [[int]]:
        new_board_str = board.split(",")
        new_board = []
        for i in range(0, 6):
            new_row = []
            for j in range(0, 6):
                new_row.append(new_board_str[i * 6 + j])
            new_board.append(new_row)
        return new_board

    def debug_print(self):
        for i in range(0, 6):
            print("%8s %8s %8s %8s %8s %8s" % (
                str(self._board[i][0].camp), str(self._board[i][1].camp),
                str(self._board[i][2].camp), str(self._board[i][3].camp),
                str(self._board[i][4].camp), str(self._board[i][5].camp)))
        print("\n")
