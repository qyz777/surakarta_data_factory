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

    @staticmethod
    def post_tactic(chess_board: [[Chess]], step_num: int) -> dict:
        """
        后手战术
        :param chess_board: 棋盘
        :param step_num: 步数
        :return:
        """
        if step_num == 0:
            p1 = chess_board[3][0]
            p2 = chess_board[3][2]
            if p1.camp == 1 or p2.camp == 1:
                return {"from": chess_board[1][1], "to": chess_board[2][2]}
            p1 = chess_board[3][5]
            p2 = chess_board[3][3]
            if p1.camp == 1 or p2.camp == 1:
                return {"from": chess_board[1][4], "to": chess_board[2][3]}
        elif step_num == 1:
            p1 = chess_board[3][0]
            p2 = chess_board[3][2]
            if p1.camp == 1 and p2.camp == 1:
                if chess_board[1][0].camp != 0 and chess_board[2][1].camp == 0:
                    return {"from": chess_board[1][0], "to": chess_board[2][1]}
            p1 = chess_board[3][5]
            p2 = chess_board[3][3]
            if p1.camp == 1 and p2.camp == 1:
                if chess_board[1][5].camp != 0 and chess_board[2][4].camp == 0:
                    return {"from": chess_board[1][5], "to": chess_board[2][4]}
        elif step_num == 2:
            p1 = chess_board[4][1]
            p2 = chess_board[5][1]
            if p1.camp == 1 and p2.camp == 0:
                if chess_board[0][1].camp != 0 and chess_board[1][1].camp == 0:
                    return {"from": chess_board[0][1], "to": chess_board[1][1]}
            p1 = chess_board[4][4]
            p2 = chess_board[5][4]
            if p1.camp == 1 and p2.camp == 0:
                if chess_board[0][4].camp != 0 and chess_board[1][4].camp == 0:
                    return {"from": chess_board[0][4], "to": chess_board[1][4]}
        return None
