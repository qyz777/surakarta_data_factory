from surakarta import game
import sys


sys.setrecursionlimit(1000000)


class Engine(object):

    def __init__(self, game_info: dict, callback):
        self._game = game.Game(1, is_debug=False, game_info=game_info)
        self._callback = callback

    def start(self):
        _, action = self._min_max_search(1)
        self._callback(action)

    # @tail_call_optimized
    def _min_max_search(self, player: int, memo: dict = None, depth: int = 0) -> (int, dict):
        if memo is None:
            memo = {}
        if player == -1:
            best_value = -10
        else:
            best_value = 10

        best_action: dict = None

        win, camp = self._game.has_winner()
        if win:
            if camp == 1:
                return -10 + depth, None
            else:
                return 10 - depth, None
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

            if player == -1:
                if value > best_value:
                    best_value, best_action = value, action
            else:
                if value < best_value:
                    best_value, best_action = value, action

        return best_value, best_action
