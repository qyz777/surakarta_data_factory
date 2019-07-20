from surakarta import game
from surakarta.chess import Chess
from nemesis.search import Search, SearchConfig
import sys
import time

sys.setrecursionlimit(1000000)

# 参考 https://www.cnblogs.com/royhoo/p/6425761.html
# todo: 还需要优化评估值

META_VALUE = 880  # 评估值总和


class DepthSearch(Search):

    def _find_best_action(self) -> (int, dict):
        self._best_action = None
        self._history_table = {}
        self._distance = 0
        value = 0
        now = time.time()
        for i in range(1, self._config.depth):
            value = self._alpha_beta_search(-META_VALUE, META_VALUE, i)
            print("depth: %d, value: %d" % (i, value))
            search_time = time.time()
            if search_time - now > 30:
                break
        return value, self._best_action

    def _alpha_beta_search(self, alpha: int, beta: int, depth: int = 5) -> int:
        """
        搜到一个深度就停止了
        :param alpha: 初始要取负无穷，表示当前搜索节点走棋一方搜索到的最好值
        :param beta: 初始要取正无穷，目前的劣势，这是对手所能承受的最坏结果。Beta值越大，表示对方劣势越明显
        :param depth: 深度
        :return:
        """
        self._best_value = alpha
        # 搜索结束返回
        if depth == 0:
            return self._chess_board_value(self._ai_camp)
        win, _ = self._game.has_winner()
        if win:
            return self._chess_board_value(self._ai_camp)

        best_move_action = None
        best_value = -META_VALUE

        all_moves = self._game.get_moves()  # 获取所有下棋招法
        all_moves = self._sort_all_moves(all_moves)  # 按照历史表排序

        for action in all_moves:
            self._game.do_move(action)  # 执行招法
            value = -self._alpha_beta_search(-beta, -self._best_value, depth - 1)
            self._game.cancel_move()  # 撤回招法

            if value > best_value:
                best_value = value
                if value > beta:
                    best_move_action = action
                    break
                if value > self._best_value:
                    self._best_value = value
                    best_move_action = action
                    if self._distance == 0:
                        self._best_action = action

        if best_value == -META_VALUE:
            return self._distance - META_VALUE

        if best_move_action is not None:
            self._update_history_table(best_move_action, depth)

        return best_value

    def _sort_all_moves(self, all_moves: [dict]):
        def take_second(e):
            return e[1]

        move_tuple_list = []
        for move in all_moves:
            v = 0
            if self._history_table.get(self._get_key(move)):
                v = self._history_table.get(self._get_key(move))
            move_tuple_list.append((move, v))
        move_tuple_list.sort(key=take_second)
        sorted_all_moves = []
        for t in move_tuple_list:
            sorted_all_moves.append(t[0])
        return sorted_all_moves

    def _update_history_table(self, action: dict, depth: int):
        key = self._get_key(action)
        value = 0
        if self._history_table.get(key):
            value += self._history_table[key]
        self._history_table.update({
            key: value + depth * depth
        })

    @staticmethod
    def _get_key(action: dict) -> str:
        return "{tag}:{from_x},{from_y}->{to_x},{to_y}".format(tag=action["from"].tag,
                                                               from_x=action["from"].x,
                                                               from_y=action["from"].y,
                                                               to_x=action["to"].x,
                                                               to_y=action["to"].y)

    @staticmethod
    def _chess_value(chess: Chess) -> int:
        x = chess.x
        y = chess.y
        # 上和下的评估值是翻转180°的
        score_top = [[0, 10, 10, 10, 10, 0],
                     [20, 50, 20, 20, 50, 20],
                     [40, 20, 40, 40, 20, 40],
                     [20, 20, 20, 20, 20, 20],
                     [30, 50, 40, 40, 50, 30],
                     [10, 20, 20, 20, 20, 10]]
        score_bottom = [[10, 20, 20, 20, 20, 10],
                        [30, 50, 40, 40, 50, 30],
                        [20, 20, 20, 20, 20, 20],
                        [40, 20, 40, 40, 20, 40],
                        [20, 50, 20, 20, 50, 20],
                        [0, 10, 10, 10, 10, 0]]
        return score_top[x][y] if chess.camp == -1 else score_bottom[x][y]

    def _chess_board_value(self, camp: int) -> int:
        value_sum = 0
        for row in self._game.chess_board:
            for chess in row:
                if chess.camp == camp:
                    value_sum += self._chess_value(chess)
        return value_sum
