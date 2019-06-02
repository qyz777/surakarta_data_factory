from surakarta import game
from excavator import setting
import sys
import random

sys.setrecursionlimit(1000000)


class Engine(object):

    def __init__(self, game_info: dict):
        self._game = game.Game(setting.ai_camp(), is_debug=False, game_info=game_info)

    def ignition(self) -> dict:
        """
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

    # 这其实是个回溯算法
    def _min_max_search(self, player: int, memo: dict = None, depth: int = 0) -> (int, dict):
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
        for action in all_moves:
            key = "{tag}:{from_x},{from_y}->{to_x},{to_y}".format(tag=action["from"].tag,
                                                                  from_x=action["from"].x,
                                                                  from_y=action["from"].y,
                                                                  to_x=action["to"].x,
                                                                  to_y=action["to"].y)
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
                    if value > best_value:
                        best_value, best_action = value, action
                else:
                    if value < best_value:
                        best_value, best_action = value, action
        return best_value, best_action
