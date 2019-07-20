from surakarta import game
from surakarta.chess import Chess
from numba import jit
import sys
import random

sys.setrecursionlimit(1000000)


class SearchConfig(object):
    depth = 2    # 1-6层之内可以接受
    win_weight = 50
    use_filter = False  # 过滤掉部分下棋位置


class Search(object):

    def __init__(self, game_info: dict, ai_camp: int, config: SearchConfig):
        self._ai_camp = ai_camp
        self._game = game.Game(self._ai_camp, is_debug=False, game_info=game_info)
        self._config = config

    def start(self) -> dict:
        """
        开始搜索
        开始进行搜索，搜不到就随机选一步
        :return: 着法
        """
        value, action = self._find_best_action()
        print("α-β剪枝搜索完成 value:%d" % value)
        if action is None:
            print("搜索错误，随机走一步")
            all_moves = self._game.get_moves()
            move = None
            for m in all_moves:
                if m["to"].tag != 0:
                    move = m
            move = random.choice(all_moves) if move is None else move
            return move
        else:
            print("搜索成功")
            return action

    def _find_best_action(self) -> (int, dict):
        """
        重写此方法添加搜索方式
        :return: (value, action)
        """
        pass

    @jit
    def filtration(self, move_list: [dict]) -> [dict]:
        """
        重写此方法添加过滤器
        :param move_list: 过滤后的着法
        :return:
        """
        pass

    @staticmethod
    def _chess_value(chess: Chess) -> int:
        """
        重写此方法设置棋子value
        :param chess: 棋子
        :return: 此棋子价值
        """
        pass

    @jit
    def _chess_board_value(self, camp: int) -> int:
        """
        重写此方法设置棋盘value
        :param camp: 阵营
        :return: 棋盘价值
        """
        pass
