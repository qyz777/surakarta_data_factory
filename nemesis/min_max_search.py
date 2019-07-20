from surakarta import game
from surakarta.chess import Chess
from nemesis.search import Search, SearchConfig
from numba import jit
import sys
import random

sys.setrecursionlimit(1000000)


class MinMaxSearch(Search):

    def __init__(self, game_info: dict, ai_camp: int, config: SearchConfig):
        super().__init__(game_info, ai_camp, config)

    def _find_best_action(self) -> (int, dict):
        return self._min_max_search(self._ai_camp)

    def _min_max_search(self, player: int, memo: dict = None, depth: int = 0) -> (int, dict):
        """
        剪枝过度可以搜到输赢结果
        α-β剪枝的本质是一个回溯算法，这里用了memo作为字典去记录走过的路径
        :param player: 玩家
        :param memo: 存储走过的路径
        :param depth: 深度
        :return: 价值和着法
        """
        if memo is None:
            memo = {}

        best_value: int = None
        best_action: dict = None

        win, camp = self._game.has_winner()
        if win:
            if camp == -self._ai_camp:
                return 10 - depth, None
            else:
                return -10 + depth, None

        all_moves = self._game.get_moves()
        all_moves = self.filtration(all_moves)
        for action in all_moves:
            key_1, key_2 = self._get_two_key(action)
            if key_1 in memo or key_2 in memo:
                continue
            self._game.do_move(action)
            memo[key_1] = 1
            memo[key_2] = 1
            value, _ = self._min_max_search(-player, memo, depth + 1)
            self._game.cancel_move()
            # value有可能为空，说明此时没有着法了
            if value is None:
                continue
            if best_value is None:
                best_value, best_action = value, action
            else:
                if player == self._ai_camp:
                    # 对于我方来说，要选择value最大的
                    if value > best_value:
                        best_value, best_action = value, action
                else:
                    # 对于对方来说，要选择value最小的
                    if value < best_value:
                        best_value, best_action = value, action
        return best_value, best_action

    @staticmethod
    def _get_two_key(action: dict) -> (str, str):
        """
        获得着法的来回的key
        :param action: 着法信息
        :return: (key_1, key_2)
        """
        str_1 = "{tag}:{from_x},{from_y}->{to_x},{to_y}".format(tag=action["from"].tag,
                                                                from_x=action["from"].x,
                                                                from_y=action["from"].y,
                                                                to_x=action["to"].x,
                                                                to_y=action["to"].y)
        str_2 = "{tag}:{to_x},{to_y}->{from_x},{from_y}".format(tag=action["from"].tag,
                                                                from_x=action["from"].x,
                                                                from_y=action["from"].y,
                                                                to_x=action["to"].x,
                                                                to_y=action["to"].y)
        return str_1, str_2

    def filtration(self, move_list: [dict]) -> [dict]:
        """
        过滤不需要的着法
        目前下棋位置包含吃子的话就把飞吃子的都过滤了
        :param move_list: 着法列表
        :return: 过滤后的着法列表
        """
        fly_move_list = []
        for move in move_list:
            if move["to"].tag != 0:
                fly_move_list.append(move)
        if len(fly_move_list) == 0:
            return move_list
        else:
            return fly_move_list
