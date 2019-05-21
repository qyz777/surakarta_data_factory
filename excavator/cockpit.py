from excavator import energy
from excavator import engine
import threading


class Cockpit(object):

    def __init__(self):
        self.__energy = energy.Energy()

    def search(self, game_info: dict, callback):
        # info = {"chess_num": chess_num, "board": game_info["board"]}
        # result = self.__energy.select_go(info)
        # if len(data_list) == 0:
        #     # 这里调用α-β剪枝搜索
        #     e = engine.Engine(game_info)
        #     return e.start()
        # return result
        # 这里调用α-β剪枝搜索
        e = engine.Engine(game_info, callback)
        t = threading.Thread(target=e.start)
        t.start()
