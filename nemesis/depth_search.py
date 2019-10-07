from surakarta import game
from surakarta.chess import Chess
from nemesis.search import Search, SearchConfig
import sys
import time
import random
from numba import jit

sys.setrecursionlimit(1000000)

# 参考 https://www.cnblogs.com/royhoo/p/6425761.html
# 百分比估值即 一方评估值/双方评估值之和

META_VALUE = 840  # 评估值总和，计算方式为所有棋子能占据的最大和
NULL_DEPTH = 2  # 空着搜索需要减去的深度值


class DepthSearch(Search):

    def _find_best_action(self) -> (int, dict):
        self._best_action = None
        self._history_table = {}
        self._distance = 0  # 水平线
        self._repeat_step = {}  # 重复局面
        self._use_percent = self._game.red_chess_num != self._game.blue_chess_num  # 是否使用百分比估值
        self._use_random = self._game.red_chess_num == self._game.blue_chess_num  # 是否使用随机性
        if self._use_percent:
            print("棋子数量不平衡，使用百分比估值")
        if self._use_random:
            print("棋子数量平衡，增加下棋随机性")
        value = 0
        now = time.time()
        for i in range(1, self._config.depth):
            value = self._alpha_beta_search(-self._percent(META_VALUE), self._percent(META_VALUE), i)
            print("depth: %d" % i)
            search_time = time.time()
            # 判断当前这步是否超时(这里其实不准确，but大概这样就行了)
            if search_time - now >= self._config.search_time:
                break
        return value, self._best_action

    @jit
    def _alpha_beta_search(self, alpha: int, beta: int, depth: int = 5, null: bool = False) -> int:
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
            if null and self._game.chess_num <= 12:
                # 执行空着，目的是确认我方是否优势
                # 残局时不进入，阈值为棋子总和小于等于12
                self._game.do_null_move()
                null_value = -self._alpha_beta_search(-beta, 1 - beta, depth - NULL_DEPTH - 1)
                self._game.cancel_null_move()
                if null_value >= beta or \
                        self._alpha_beta_search(alpha, beta, depth - NULL_DEPTH) >= beta:
                    return null_value

        # 搜索结束返回
        if depth == 0:
            return self._get_real_chess_board_value()
        win, _ = self._game.has_winner()
        if win:
            return self._get_real_chess_board_value()

        best_move_action = None
        best_value = -self._percent(META_VALUE)

        all_moves = self._game.get_moves()  # 获取所有下棋招法
        all_moves = self._filter_walk_step_if_need(all_moves)
        all_moves = self._sort_all_moves(all_moves)  # 按照历史表排序

        for action in all_moves:
            self._game.do_move(action)  # 执行招法
            self._distance += 1
            value = -self._alpha_beta_search(-beta, -self._step_best_value, depth - 1, True)
            if self._use_random:
                value += self._random_value()
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

        if best_value == -self._percent(META_VALUE):
            return self._percent(self._distance - META_VALUE)

        if best_move_action is not None:
            self._update_history_table(best_move_action, depth)

        return best_value

    @jit
    def _search_fly(self, alpha: int, beta: int) -> int:
        """
        在搜索的叶子节点之下调用，只搜索吃子着法
        :param alpha: alpha值
        :param beta: beta值
        :return: 最大估值
        """
        self._fly_best_value = alpha
        value = self._percent(self._distance - META_VALUE)
        if value >= beta:
            return value
        # 检查重复局面
        repeat_value = self._is_repeat(self._game.chess_board)
        if repeat_value > 0:
            # 重复局面直接取出value返回
            return repeat_value
        # 检查是否有输赢或检查是否超出最大搜索深度(暂时就先写个32)
        win, _ = self._game.has_winner()
        if win or self._distance >= 32:
            return self._get_real_chess_board_value()

        best_value = -self._percent(META_VALUE)
        value = self._get_real_chess_board_value()
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

        return self._percent(self._distance - META_VALUE) if best_value == -self._percent(META_VALUE) else best_value

    @jit
    def _sort_all_moves(self, all_moves: [dict]):
        move_tuple_list = []
        for move in all_moves:
            v = 0
            if self._history_table.get(self._get_key(move)):
                v = self._history_table.get(self._get_key(move))
            move_tuple_list.append((move, v))
        move_tuple_list.sort(key=self.__take_second)
        sorted_all_moves = []
        for t in move_tuple_list:
            sorted_all_moves.append(t[0])
        return sorted_all_moves

    @staticmethod
    def __take_second(e):
        return e[1]

    def _update_history_table(self, action: dict, depth: int):
        key = self._get_key(action)
        value = 0
        if self._history_table.get(key):
            value += self._history_table[key]
        self._history_table.update({
            key: value + depth * depth
        })

    @jit
    def _update_repeat_step(self, chess_board: [[Chess]], value):
        chess_list = []
        for row in chess_board:
            for c in row:
                chess_list.append(str(c.camp))
        chess_list_str = ",".join(chess_list)
        self._repeat_step.update({chess_list_str: value})

    @jit
    def _is_repeat(self, chess_board: [[Chess]]) -> int:
        chess_list = []
        for row in chess_board:
            for c in row:
                chess_list.append(str(c.camp))
        chess_list_str = ",".join(chess_list)
        return self._repeat_step[chess_list_str] if self._repeat_step.get(chess_list_str) else 0

    def _get_real_chess_board_value(self):
        """
        得到棋盘评估值，在百分比估值下和绝对值估值下返回不同
        :return: 估值
        """
        if self._use_percent:
            my_score = self._chess_board_value(self._ai_camp)
            other_score = self._chess_board_value(-self._ai_camp)
            return self._percent(my_score, my_score + other_score)
        else:
            return self._chess_board_value(self._ai_camp)

    def _percent(self, value=None, sum_value=0) -> float or int:
        if self._use_percent:
            return value / META_VALUE if sum_value == 0 else value / sum_value
        else:
            return value

    @staticmethod
    def _random_value():
        """
        棋子数量相等时获取每一个节点估值的随机值
        -5~5看起来已经很够了
        :return: 随机值
        """
        return random.uniform(-5, 5)

    @jit
    def _filtration(self, move_list: [dict]) -> [dict]:
        fly_move_list = []
        for move in move_list:
            if move["to"].tag != 0:
                fly_move_list.append(move)
        if len(fly_move_list) == 0:
            return []
        else:
            return fly_move_list

    @jit
    def _filter_walk_step_if_need(self, move_list: [dict]) -> [dict]:
        """
        如果开启配置，则把walk类型的着法去除
        前提是有吃子着法
        :param move_list: 着法列表
        :return: 着法列表
        """
        if not self._config.use_filter:
            return move_list
        fly_move_list = []
        for move in move_list:
            if move["to"].tag != 0:
                fly_move_list.append(move)
        if len(fly_move_list) == 0:
            return move_list
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
