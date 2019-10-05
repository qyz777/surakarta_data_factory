from nemesis.db import DB
from nemesis.search import SearchConfig, SearchType
from nemesis.build_search import build
from nemesis.tactics import Tactics
from surakarta.chess import Chess
from surakarta.game import Game
import threading
from numba import jit


class Core(object):

    def __init__(self):
        self.ai_camp = -1
        self._is_use_db = False
        self._is_use_tactics = True
        self.is_first = False

    def playing(self, game_info: dict, callback):
        """
        下棋
        α-β剪枝搜索 or 数据库搜索
        :param game_info: 游戏信息
        :param callback: 回调
        :return:
        """
        thread = threading.Thread(target=self._playing, args=(game_info, callback))
        thread.start()

    def _playing(self, game_info: dict, callback):
        step_num = game_info["step_num"] / 2
        if self._is_use_tactics:
            if self.is_first and step_num < 3:
                tactic = Tactics.pre_tactic(game_info["board"], step_num)
                if tactic is not None:
                    callback(tactic)
                    return

        db = DB(self.ai_camp)
        info = {"chess_num": game_info["red_num"] + game_info["blue_num"],
                "board": self._zip_board(game_info["board"])}
        d = None
        if self._is_use_db:
            result = db.select_go(info)
            d = self._setup_chess_from_row(result, game_info["board"])
        if d is None:
            print("选择α-β剪枝搜索")
            config = self._get_search_config()
            search = build(game_info, self.ai_camp, config)
            move = search.start()
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

    @staticmethod
    def _get_search_config() -> SearchConfig:
        """
        这里改AI搜索配置!
        :return: 搜索配置
        """
        config = SearchConfig()
        config.use_filter = True
        config.search_type = SearchType.DEPTH
        return config
