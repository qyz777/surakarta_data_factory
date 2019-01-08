from surakarta.play_manager import PlayManager
from surakarta.chess import Chess
import copy
import random


class Game(object):

    def __init__(self, is_debug=False):
        self.__is_debug = is_debug
        self.__boards = []
        self.__current_player = None
        self.__red = 12
        self.__blue = 12
        self.__board = None
        self.__last_move = None
        self.__camp = 0
        self.__player = [1, 2]
        self.__play_manager = PlayManager()

    def start_play(self):
        self.__reset_board()
        self.__camp = random.choice([-1, 1])
        while True:
            moves = self.__get_moves()
            move = random.choice(moves)
            self.__do_move(move)
            if self.__is_debug:
                self.__debug_print()
            is_win, winner = self.__has_winner()
            if is_win:
                break
        return self.__boards

    def __reset_board(self):
        self.__red = 12
        self.__blue = 12
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
        self.__board = copy.deepcopy(chess_lists)

    def __do_move(self, info):
        tread = info['from']
        can_move = info['to']
        tag = tread.tag
        short_a = self.__board[tread.x][tread.y]
        short_camp = short_a.camp
        short_a.tag = 0
        short_a.camp = 0
        self.__board[tread.x][tread.y] = short_a

        short_b = self.__board[can_move.x][can_move.y]
        if short_b.camp == -1:
            self.__red -= 1
        if short_b.camp == 1:
            self.__blue -= 1
        short_b.tag = tag
        short_b.camp = short_camp
        self.__board[can_move.x][can_move.y] = short_b
        # 修改阵营
        self.__camp = -self.__camp
        new_board = copy.deepcopy(self.__board)
        self.__boards.append({"player": self.__current_player, "board": new_board})
        self.__current_player = (
            self.__player[0] if self.__current_player == self.__player[1] else self.__player[1]
        )
        # 上一个局面吃子的位置，没有则不记录
        if can_move.camp + tread.camp == 0:
            self.__last_move = info
        else:
            self.__last_move = None

    # 1 蓝方赢 -1 红方赢
    def __has_winner(self):
        if self.__red <= 0:
            return True, 1
        if self.__blue <= 0:
            return True, -1
        return False, 0

    def __get_moves(self):
        return self.__play_manager.get_moves(self.__camp, self.__board)

    def __debug_print(self):
        for i in range(0, 6):
            print("%8s %8s %8s %8s %8s %8s" % (
                str(self.__board[i][0].camp), str(self.__board[i][1].camp),
                str(self.__board[i][2].camp), str(self.__board[i][3].camp),
                str(self.__board[i][4].camp), str(self.__board[i][5].camp)))
        print("\n")
