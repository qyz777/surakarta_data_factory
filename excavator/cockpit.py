from excavator.energy import Energy
from excavator.engine import Engine
from surakarta.chess import Chess
from surakarta.game import Game
import threading
from numba import jit


class Cockpit(object):

    def __init__(self):
        self.ai_camp = -1
        self._is_use_db = False

    def scoop(self, game_info: dict, callback):
        """
        挖
        α-β剪枝搜索 or 数据库搜索
        :param game_info: 游戏信息
        :param callback: 回调
        :return:
        """
        thread = threading.Thread(target=self._search, args=(game_info, callback))
        thread.start()

    def _search(self, game_info: dict, callback):
        energy = Energy(self.ai_camp)
        info = {"chess_num": game_info["red_num"] + game_info["blue_num"],
                "board": self._zip_board(game_info["board"])}
        d = None
        if self._is_use_db:
            result = energy.select_go(info)
            d = self._setup_chess_from_row(result, game_info["board"])
        if d is None:
            print("选择α-β剪枝搜索")
            e = Engine(game_info, self.ai_camp)
            move = e.ignition()
            callback(move)
        else:
            print("选择数据库搜索")
            callback(d)

    @staticmethod
    def _setup_chess_from_row(row: tuple, board: [[Chess]]) -> dict:
        if row is None or len(row) == 0:
            return None
        from_chess = Chess()
        from_chess.x = row[6]
        from_chess.y = row[7]
        from_chess.tag = board[row[6]][row[7]].tag
        if from_chess.tag == 0:
            return None
        to_chess = Chess()
        to_chess.x = row[8]
        to_chess.y = row[9]
        to_chess.tag = board[row[8]][row[9]].tag
        return {"from": from_chess, "to": to_chess}

    @staticmethod
    @jit
    def _zip_board(board: [[Chess]]) -> str:
        zip_list = []
        for i in range(0, 6):
            for j in range(0, 6):
                zip_list.append(str(board[i][j].camp))
        return ",".join(zip_list)