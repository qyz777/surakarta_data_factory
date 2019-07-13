from surakarta.chess import Chess


class Tactics(object):

    @staticmethod
    def pre_tactic(chess_board: [[Chess]], step_num: int) -> dict:
        """
        先手战术，采用前三步主动进攻的方式压制对手
        :param chess_board:棋盘
        :param step_num:下棋的步数
        :return:
        """
        info: dict = None
        if step_num == 0:
            info = {"from": chess_board[4][2], "to": chess_board[3][2]}
        elif step_num == 1:
            info = {"from": chess_board[4][0], "to": chess_board[3][0]}
        elif step_num == 2:
            info = {"from": chess_board[5][1], "to": chess_board[4][2]}
        return info
