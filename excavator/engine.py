from surakarta import game
from surakarta.chess import Chess
from numba import jit
import sys
import random

sys.setrecursionlimit(1000000)

SEARCH_DEPTH = 5
SEARCH_TYPE = 1
SEARCH_WIN_WEIGHT = 50


class Engine(object):

    def __init__(self, game_info: dict, ai_camp: int):
        self._ai_camp = ai_camp
        self._game = game.Game(self._ai_camp, is_debug=False, game_info=game_info)

    def ignition(self) -> dict:
        """
        点火
        开始进行α-β搜索，搜不到就随机选一步
        :return: 着法
        """
        if SEARCH_TYPE == 0:
            value, action = self._min_max_search_1(self._ai_camp)
        else:
            value, action = self._min_max_search_2(self._ai_camp)
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

    def _min_max_search_1(self, player: int, memo: dict = None, depth: int = 0) -> (int, dict):
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
        all_moves = self._filtration(all_moves)
        for action in all_moves:
            key_1, key_2 = self._get_two_key(action)
            if key_1 in memo or key_2 in memo:
                continue
            self._game.do_move(action)
            memo[key_1] = 1
            memo[key_2] = 1
            value, _ = self._min_max_search_1(-player, memo, depth + 1)
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

    def _min_max_search_2(self, player: int, memo: dict = None, depth: int = 0) -> (int, dict):
        """
        搜到一个深度就停止了
        :param player: 玩家
        :param memo: 存储走过的路径
        :param depth: 深度
        :return: 价值和着法
        """
        # 适当时机清理memo
        if memo is None or (depth + 1) % 2 == 0:
            memo = {}

        best_value: int = None
        best_action: dict = None

        win, camp = self._game.has_winner()
        if win:
            if camp == -self._ai_camp:
                return (10 - depth) * SEARCH_WIN_WEIGHT, None
            else:
                return (-10 + depth) * SEARCH_WIN_WEIGHT, None
        elif depth == SEARCH_DEPTH:
            return self._chess_board_value(camp), None

        all_moves = self._game.get_moves()
        for action in all_moves:
            key_1, key_2 = self._get_two_key(action)
            if key_1 in memo or key_2 in memo:
                continue
            self._game.do_move(action)
            memo[key_1] = 1
            memo[key_2] = 1
            value, _ = self._min_max_search_2(-player, memo, depth + 1)
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
    def _evaluate(chessboard: [[Chess]], camp: int) -> int:
        score = 0
        for row in chessboard:
            for chess in row:
                if chess.camp == camp:
                    score += 1
        return score

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

    @jit
    def _filtration(self, move_list: [dict]) -> [dict]:
        """
        过滤不需要的着法
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

    @staticmethod
    def _get_red_attack_list() -> [(int, int)]:
        return [(3, 1), (3, 4), (4, 2), (4, 3)]

    @staticmethod
    def _get_blue_attack_list() -> [(int, int)]:
        return [(1, 2), (1, 3), (2, 1), (2, 4)]

    @staticmethod
    def _chess_value(chess: Chess) -> int:
        x = chess.x
        y = chess.y
        score = [[0, 10, 10, 10, 10, 0],
                 [20, 50, 20, 20, 50, 20],
                 [40, 20, 40, 40, 20, 40],
                 [40, 20, 40, 40, 20, 40],
                 [20, 50, 20, 20, 50, 20],
                 [0, 10, 10, 10, 10, 0]]
        return score[x][y]

    @jit
    def _chess_board_value(self, camp: int) -> int:
        res = 0
        for row in self._game.chess_board:
            for chess in row:
                if chess.camp == camp:
                    res += self._chess_value(chess)
        return res
