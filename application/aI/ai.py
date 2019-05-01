from helper import db_helper
from surakarta import chess


class AI(object):

    def __init__(self):
        self.__helper = db_helper.DBHelper()

    def search(self, chess_num: int, chess_board: [[]]) -> dict:
        zip_board = self.__zip_board(chess_board)
        info = {"chess_num": chess_num, "board": zip_board}
        data_list = self.__helper.select_go(info)
        result = None
        if len(data_list) == 0:
            # todo: 选择下一个要下的棋子，这里可以调搜索
            print("找不到下一步要下的棋子")
        else:
            result = self.__find_max(data_list)
        return result

    @staticmethod
    def __find_max(data_list: []) -> dict:
        return max(data_list["prob"])

    @staticmethod
    def __zip_board(board: [[]]) -> [[]]:
        zip_list = []
        for i in range(0, 6):
            for j in range(0, 6):
                zip_list.append(str(board[i][j].camp))
        return ",".join(zip_list)