from surakarta import game
from surakarta.chess import Chess
from excavator import setting
from numba import jit
import sys
import random

sys.setrecursionlimit(1000000)


class Engine(object):

    def __init__(self, game_info: dict):
        self._game = game.Game(setting.ai_camp(), is_debug=False, game_info=game_info)

    def ignition(self) -> dict:
        """
        点火
        开始进行α-β搜索，搜不到就随机选一步
        :return: 着法
        """
        _, action = self._min_max_search(setting.ai_camp())
        print("α-β剪枝搜索完成")
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

    def _min_max_search(self, player: int, memo: dict = None, depth: int = 0) -> (int, dict):
        """
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
            if camp == 1:
                return 10 - depth, None
            else:
                return -10 + depth, None
        all_moves = self._game.get_moves()
        all_moves = self._filtration(all_moves, player)
        for action in all_moves:
            key = self._get_a_key(action)
            if key in memo:
                continue
            self._game.do_move(action)
            memo[key] = 1
            value, _ = self._min_max_search(-player, memo, depth + 1)
            self._game.cancel_move()
            # value有可能为空，说明此时没有着法了
            if value is None:
                continue
            if best_value is None:
                best_value, best_action = value, action
            else:
                if player == -1:
                    # 对于我方来说，要选择value最大的
                    if value > best_value:
                        best_value, best_action = value, action
                else:
                    # 对于对方来说，要选择value最小的
                    if value < best_value:
                        best_value, best_action = value, action
        return best_value, best_action

    @staticmethod
    def _evaluate(chessboard: [[Chess]], camp: int) -> int:
        score = 0
        for row in chessboard:
            for chess in row:
                if chess.camp == camp:
                    score += 1
        return score

    @staticmethod
    def _get_a_key(action: dict) -> str:
        return "{tag}:{from_x},{from_y}->{to_x},{to_y}".format(tag=action["from"].tag,
                                                               from_x=action["from"].x,
                                                               from_y=action["from"].y,
                                                               to_x=action["to"].x,
                                                               to_y=action["to"].y)

    @jit
    def _filtration(self, move_list: [dict], player: int) -> [dict]:
        """
        过滤不需要的着法
        :param move_list: 着法列表
        :return: 过滤后的着法列表
        """
        my_attack_list = self._get_red_attack_list() if player == -1 else self._get_blue_attack_list()
        new_move_list = []
        fly_move_list = []
        for move in move_list:
            if (move["to"].x, move["to"].y) in my_attack_list:
                new_move_list.append(move)
            elif move["to"].tag != 0:
                fly_move_list.append(move)
        if len(fly_move_list) == 0:
            return move_list
        else:
            new_move_list.extend(fly_move_list)
            return fly_move_list

    @staticmethod
    def _get_red_attack_list() -> [(int, int)]:
        return [(3, 1), (3, 4), (4, 2), (4, 3)]

    @staticmethod
    def _get_blue_attack_list() -> [(int, int)]:
        return [(1, 2), (1, 3), (2, 1), (2, 4)]
