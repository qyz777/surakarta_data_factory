import copy
from surakarta import chess

from numba import jit


class PlayManager(object):

    def __init__(self):
        self.board = None
        self.fly_x = 0
        self.fly_y = 0
        self.fly_path = []

    # 调用这个获取下棋位置 返回的是字典数组{'from', 'to'} from是棋子 to是下棋的位置 都为chess对象
    def get_moves(self, camp: int, board: [[chess.Chess]]) -> [dict]:
        if camp == 0:
            raise RuntimeError("Camp must be - 1 or 1!!!")

        self.board = copy.deepcopy(board)
        self.fly_x = 0
        self.fly_y = 0
        self.fly_path = []
        fly_moves = self.create_fly_moves(camp)
        if len(fly_moves) > 0:
            return fly_moves
        walk_moves = self.create_walk_moves(camp)
        walk_moves.extend(fly_moves)
        return walk_moves

    def get_game_moves(self, chess: chess.Chess, board: [[chess.Chess]]) -> [dict]:
        self.board = board
        move_list = []
        walk_list = self._walk_engine(chess.x, chess.y)
        if len(walk_list) > 0:
            for w in walk_list:
                move_list.append({"from": chess, "to": w})
        fly_list = self._begin_fly(chess.x, chess.y, chess.camp)
        if len(fly_list) > 0:
            for fly in fly_list:
                move_list.append({"from": chess, "to": fly[-1]})
        return move_list

    @jit
    def create_walk_moves(self, camp: int) -> [chess.Chess]:
        move_list = []
        for i in range(0, 6):
            for j in range(0, 6):
                p = self.board[i][j]
                if p.camp == camp:
                    walk_list = self._walk_engine(p.x, p.y)
                    for w in walk_list:
                        d = {"from": p, "to": w}
                        move_list.append(d)
        return copy.deepcopy(move_list)

    @jit
    def create_fly_moves(self, camp: int) -> [chess.Chess]:
        move_list = []
        for i in range(0, 6):
            for j in range(0, 6):
                p = self.board[i][j]
                if p.camp == camp:
                    fly_list = self._begin_fly(p.x, p.y, p.camp)
                    for fly in fly_list:
                        move_list.append({"from": p, "to": fly[-1]})
        return copy.deepcopy(move_list)

    def _begin_fly(self, x, y, camp):
        finish_fly_path = []
        for i in range(0, 4):
            self.fly_x = x
            self.fly_y = y
            self._fly_engine(x, y, i, camp, False)
            if self.fly_path is not None and len(self.fly_path) > 0:
                finish_fly_path.append(copy.deepcopy(self.fly_path))
                self.fly_path = []
        return copy.deepcopy(finish_fly_path)

    def _can_fly(self, orientation):
        # 向下
        if orientation == 0:
            self.fly_x -= 1
            if self.fly_x < 0:
                self.fly_x += 1
                return False
            else:
                return True
        # 向右
        if orientation == 1:
            self.fly_y += 1
            if self.fly_y > 5:
                self.fly_y -= 1
                return False
            else:
                return True
        # 向上
        if orientation == 2:
            self.fly_x += 1
            if self.fly_x > 5:
                self.fly_x -= 1
                return False
            else:
                return True
        # 向左
        if orientation == 3:
            self.fly_y -= 1
            if self.fly_y < 0:
                self.fly_y += 1
                return False
            else:
                return True

        return False

    def _fly_engine(self, x, y, orientation, camp, already_fly):
        if (self.fly_x == 0 and self.fly_y == 0) or (self.fly_x == 5 and self.fly_y == 0) or \
                (self.fly_x == 0 and self.fly_y == 5) or (self.fly_x == 5 and self.fly_y == 5):
            return

        while self._can_fly(orientation):
            p = self.board[self.fly_x][self.fly_y]
            if p.camp != 0:
                if p.camp + camp == 0:
                    if already_fly:
                        # 可以飞了
                        self.fly_path.append(p)
                    else:
                        self.fly_path = []
                    return
                else:
                    if self.fly_x == x & self.fly_y == y:
                        if len(self.fly_path) < 6:
                            continue
                        else:
                            return
                    else:
                        self.fly_path = []
                        return

        if (self.fly_x == 0 and self.fly_y == 0) or (self.fly_x == 5 and self.fly_y == 0) or \
                (self.fly_x == 0 and self.fly_y == 5) or (self.fly_x == 5 and self.fly_y == 5):
            return

        # node是在进圈的那个点
        node = self.board[self.fly_x][self.fly_y]
        self.fly_path.append(node)

        # 获取绕完圈出口的点
        next_node_x, next_node_y = self._pathway_table(copy.deepcopy(self.fly_x), copy.deepcopy(self.fly_y))
        if next_node_x != -1 and next_node_y != -1:
            self.fly_x = next_node_x
            self.fly_y = next_node_y

        next_node = self.board[self.fly_x][self.fly_y]
        if next_node.camp != 0:
            if next_node.camp + camp == 0:
                # 可以飞了
                self.fly_path.append(next_node)
            else:
                self.fly_path = []
            return
        else:
            orientation = self._direction_table(self.fly_x, self.fly_y)
            self._fly_engine(x, y, orientation, camp, True) # bug

    def _walk_engine(self, x, y):
        array = []
        if (x - 1 >= 0) & (y - 1 >= 0) & (x - 1 < 6) & (y - 1 < 6):
            if self.board[x - 1][y - 1].camp == 0:
                array.append(self.board[x - 1][y - 1])
        if (x - 1 >= 0) & (y >= 0) & (x - 1 < 6) & (y < 6):
            if self.board[x - 1][y].camp == 0:
                array.append(self.board[x - 1][y])
        if (x - 1 >= 0) & (y + 1 >= 0) & (x - 1 < 6) & (y + 1 < 6):
            if self.board[x - 1][y + 1].camp == 0:
                array.append(self.board[x - 1][y + 1])
        if (x >= 0) & (y - 1 >= 0) & (x < 6) & (y - 1 < 6):
            if self.board[x][y - 1].camp == 0:
                array.append(self.board[x][y - 1])
        if (x >= 0) & (y + 1 >= 0) & (x < 6) & (y + 1 < 6):
            if self.board[x][y + 1].camp == 0:
                array.append(self.board[x][y + 1])
        if (x + 1 >= 0) & (y - 1 >= 0) & (x + 1 < 6) & (y - 1 < 6):
            if self.board[x + 1][y - 1].camp == 0:
                array.append(self.board[x + 1][y - 1])
        if (x + 1 >= 0) & (y >= 0) & (x + 1 < 6) & (y < 6):
            if self.board[x + 1][y].camp == 0:
                array.append(self.board[x + 1][y])
        if (x + 1 >= 0) & (y + 1 >= 0) & (x + 1 < 6) & (y + 1 < 6):
            if self.board[x + 1][y + 1].camp == 0:
                array.append(self.board[x + 1][y + 1])
        return array

    @classmethod
    def _pathway_table(cls, x, y):
        if x == 0:
            if y == 1:
                return 1, 0
            if y == 2:
                return 2, 0
            if y == 3:
                return 2, 5
            if y == 4:
                return 1, 5
        if x == 1:
            if y == 0:
                return 0, 1
            if y == 5:
                return 0, 4
        if x == 2:
            if y == 0:
                return 0, 2
            if y == 5:
                return 0, 3
        if x == 3:
            if y == 0:
                return 5, 2
            if y == 5:
                return 5, 3
        if x == 4:
            if y == 0:
                return 5, 1
            if y == 5:
                return 5, 4
        if x == 5:
            if y == 1:
                return 4, 0
            if y == 2:
                return 3, 0
            if y == 3:
                return 3, 5
            if y == 4:
                return 4, 5
        return -1, -1

    @classmethod
    def _direction_table(cls, x, y):
        if x == 0:
            if (y == 1) or (y == 2) or (y == 3) or (y == 4):
                return 2
        if x == 1:
            if y == 0:
                return 1
            if y == 5:
                return 3
        if x == 2:
            if y == 0:
                return 1
            if y == 5:
                return 3
        if x == 3:
            if y == 0:
                return 1
            if y == 5:
                return 3
        if x == 4:
            if y == 0:
                return 1
            if y == 5:
                return 3
        if x == 5:
            if (y == 1) or (y == 2) or (y == 3) or (y == 4):
                return 0
        return -1