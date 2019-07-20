from surakarta import game
from surakarta.chess import Chess
from nemesis.search import Search, SearchConfig
import sys
import time

sys.setrecursionlimit(1000000)

# 参考 https://www.cnblogs.com/royhoo/p/6425761.html
# todo: 还需要优化评估值、完善空着、置换表

META_VALUE = 960  # 评估值总和


class DepthSearch(Search):

    def _find_best_action(self) -> (int, dict):
        self._best_action = None
        self._history_table = {}
        self._distance = 0  # 水平线
        self._repeat_step = {}  # 重复局面
        value = 0
        # now = time.time()
        for i in range(1, self._config.depth):
            value = self._alpha_beta_search(-META_VALUE, META_VALUE, i)
            print("depth: %d, value: %d" % (i, value))
            # search_time = time.time()
            # if search_time - now > 30:
            #     break
        return value, self._best_action

    def _alpha_beta_search(self, alpha: int, beta: int, depth: int = 5) -> int:
        """
        α-β搜索，搜到一个深度就会停止
        :param alpha: 初始要取负无穷，表示当前搜索节点走棋一方搜索到的最好值
        :param beta: 初始要取正无穷，目前的劣势，这是对手所能承受的最坏结果。Beta值越大，表示对方劣势越明显
        :param depth: 深度
        :return: 最大估值
        """
        self._step_best_value = alpha

        if self._distance > 0:
            if depth <= 0:
                # 此时可以继续往下搜到底，但是只搜吃子着法
                return self._search_fly(self._step_best_value, beta)
            # 检查重复局面
            repeat_value = self._is_repeat(self._game.chess_board)
            if repeat_value > 0:
                # 重复局面直接取出value返回
                return repeat_value

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
            self._distance += 1
            value = -self._alpha_beta_search(-beta, -self._step_best_value, depth - 1)
            self._game.cancel_move()  # 撤回招法
            self._distance -= 1

            if value > best_value:
                best_value = value
                if value > beta:
                    best_move_action = action
                    break
                if value > self._step_best_value:
                    self._step_best_value = value
                    best_move_action = action
                    if self._distance == 0:
                        self._best_action = action

        if best_value == -META_VALUE:
            return self._distance - META_VALUE

        if best_move_action is not None:
            self._update_history_table(best_move_action, depth)

        return best_value

    def _search_fly(self, alpha: int, beta: int) -> int:
        """
        在搜索的叶子节点之下调用，只搜索吃子着法
        :param alpha: alpha值
        :param beta: beta值
        :return: 最大估值
        """
        self._fly_best_value = alpha
        value = self._distance - META_VALUE
        if value >= beta:
            return value
        # 检查重复局面
        repeat_value = self._is_repeat(self._game.chess_board)
        if repeat_value > 0:
            # 重复局面直接取出value返回
            return repeat_value
        # 检查是否有输赢
        win, _ = self._game.has_winner()
        if win:
            return self._chess_board_value(self._ai_camp)
        # 检查是否超出最大搜索深度，暂时就先写个32吧
        if self._distance >= 32:
            return self._chess_board_value(self._ai_camp)

        best_value = -META_VALUE
        value = self._chess_board_value(self._ai_camp)
        if value > best_value:
            if value > beta:
                return value
            best_value = value
            self._fly_best_value = max(value, self._fly_best_value)
        all_moves = self._game.get_moves()  # 获取所有下棋招法
        all_moves = self._filtration(all_moves)  # 过滤除飞行棋子之外的棋子
        all_moves = self._sort_all_moves(all_moves)  # 排序
        for action in all_moves:
            self._game.do_move(action)  # 执行招法
            self._distance += 1
            value = -self._search_fly(-beta, -self._fly_best_value)
            self._game.cancel_move()  # 撤回招法
            self._distance -= 1

            if value > best_value:
                if value >= beta:
                    return value
                best_value = value
                self._fly_best_value = max(value, self._fly_best_value)

        return self._distance - META_VALUE if best_value == -META_VALUE else best_value

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

    def _update_repeat_step(self, chess_board: [[Chess]], value):
        chess_list = []
        for row in chess_board:
            for c in row:
                chess_list.append(str(c.camp))
        chess_list_str = ",".join(chess_list)
        self._repeat_step.update({chess_list_str: value})

    def _is_repeat(self, chess_board: [[Chess]]) -> int:
        chess_list = []
        for row in chess_board:
            for c in row:
                chess_list.append(str(c.camp))
        chess_list_str = ",".join(chess_list)
        return self._repeat_step[chess_list_str] if self._repeat_step.get(chess_list_str) else 0

    def _filtration(self, move_list: [dict]) -> [dict]:
        fly_move_list = []
        for move in move_list:
            if move["to"].tag != 0:
                fly_move_list.append(move)
        if len(fly_move_list) == 0:
            return []
        else:
            return fly_move_list

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
                     [40, 20, 40, 40, 20, 40],
                     [30, 50, 40, 40, 50, 30],
                     [10, 20, 20, 20, 20, 10]]
        score_bottom = [[10, 20, 20, 20, 20, 10],
                        [30, 50, 40, 40, 50, 30],
                        [40, 20, 40, 40, 20, 40],
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
