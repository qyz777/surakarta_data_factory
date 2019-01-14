import copy

from numba import jit


class PlayManager(object):

    def __init__(self):
        self.board = None
        self.flyX = 0
        self.flyY = 0
        self.flyPath = []

    # 调用这个获取下棋位置 返回的是字典数组{'from', 'to'} from是棋子 to是下棋的位置 都为chess对象
    def get_moves(self, camp, board):
        if camp == 0:
            raise RuntimeError("Camp must be - 1 or 1!!!")

        self.board = copy.deepcopy(board)
        self.flyX = 0
        self.flyY = 0
        self.flyPath = []
        fly_moves = self.create_fly_moves(camp)
        walk_moves = self.create_walk_moves(camp)
        walk_moves.extend(fly_moves)
        return walk_moves

    def get_game_moves(self, chess, board):
        self.board = board
        walk_array = []
        short_walk = self.__walk_engine(chess.x, chess.y)
        if len(short_walk) > 0:
            for wp in short_walk:
                d = {"from": chess, "to": wp}
                walk_array.append(d)
        short_fly = self.__begin_fly(chess.x, chess.y, chess.camp)
        if len(short_fly) > 0:
            for f in short_fly:
                cm = f[-1]
                d = {"from": chess, "to": cm}
                walk_array.append(d)
        return walk_array

    @jit
    def create_walk_moves(self, camp):
        walk_array = []
        for i in range(0, 6):
            for j in range(0, 6):
                p = self.board[i][j]
                if p.camp == camp:
                    short_walk = self.__walk_engine(p.x, p.y)
                    if len(short_walk) > 0:
                        for wp in short_walk:
                            d = {"from": p, "to": wp}
                            walk_array.append(d)
        return copy.deepcopy(walk_array)

    @jit
    def create_fly_moves(self, camp):
        fly_array = []
        for i in range(0, 6):
            for j in range(0, 6):
                p = self.board[i][j]
                if p.camp == camp:
                    short_fly = self.__begin_fly(p.x, p.y, p.camp)
                    if len(short_fly) > 0:
                        for f in short_fly:
                            cm = f[-1]
                            d = {"from": p, "to": cm}
                            fly_array.append(d)
        return copy.deepcopy(fly_array)

    def __begin_fly(self, x, y, camp):
        finish_fly_path = []
        for i in range(0, 4):
            self.flyX = x
            self.flyY = y
            short_array = self.__fly_engine(x, y, i, camp, False)
            if short_array is not None:
                finish_fly_path.append(short_array)
            self.fly_path = []
        return copy.deepcopy(finish_fly_path)

    def __can_fly(self, orientation):
        if orientation == 0:
            self.flyX -= 1
            if self.flyX < 0:
                self.flyX += 1
                return False
            else:
                return True
        if orientation == 1:
            self.flyY += 1
            if self.flyY > 5:
                self.flyY -= 1
                return False
            else:
                return True
        if orientation == 2:
            self.flyX += 1
            if self.flyX > 5:
                self.flyX -= 1
                return False
            else:
                return True
        if orientation == 3:
            self.flyY -= 1
            if self.flyY < 0:
                self.flyY += 1
                return False
            else:
                return True

        return False

    def __fly_engine(self, x, y, orientation, camp, already_fly):
        if (self.flyX == 0 and self.flyY == 0) or (self.flyX == 5 and self.flyY == 0) or \
                (self.flyX == 0 and self.flyY == 5) or (self.flyX == 5 and self.flyY == 5):
            return

        while self.__can_fly(orientation):
            p = self.board[self.flyX][self.flyY]
            if p.camp != 0:
                if p.camp + camp == 0:
                    if already_fly:
                        self.flyPath.append(p)
                        # 可以飞了
                        return copy.deepcopy(self.flyPath)
                    else:
                        self.flyPath = []
                        return
                else:
                    if self.flyX == x & self.flyY == y:
                        if len(self.flyPath) < 6:
                            continue
                        else:
                            return
                    else:
                        self.flyPath = []
                        return

        if (self.flyX == 0 and self.flyY == 0) or (self.flyX == 5 and self.flyY == 0) or \
                (self.flyX == 0 and self.flyY == 5) or (self.flyX == 5 and self.flyY == 5):
            return

        pp = self.board[self.flyX][self.flyY]
        self.flyPath.append(pp)

        short_x, short_y = self.__pathway_table(copy.deepcopy(self.flyX), copy.deepcopy(self.flyY))
        if short_x != 9 and short_y != 9:
            self.flyX = short_x
            self.flyY = short_y

        ppp = self.board[self.flyX][self.flyY]
        if ppp.camp != 0:
            if ppp.camp + camp == 0:
                self.flyPath.append(ppp)
                # 可以飞了
                return copy.deepcopy(self.flyPath)
            else:
                self.flyPath = []
                return
        else:
            orientation = self.__direction_table(self.flyX, self.flyY)
            self.__fly_engine(x, y, orientation, camp, True)
        return

    def __walk_engine(self, x, y):
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
    def __pathway_table(cls, x, y):
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
        return 9, 9

    @classmethod
    def __direction_table(cls, x, y):
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