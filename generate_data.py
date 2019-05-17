from surakarta import game
from helper import db_helper
import os
import gc
from multiprocessing import Process, Pool


PLAY_COUNT = 3


def remove_lose_data(data_list, winner_camp):
    win_data = []
    for info in data_list:
        if info["camp"] == winner_camp:
            win_data.append(info)
    return win_data


def start():
    if os.path.exists('./data.db'):
        db = db_helper.DBHelper("data.db")
    else:
        db = db_helper.DBHelper("data.db")
        db.create_tables()
    g = game.Game(is_debug=False)
    for i in range(0, PLAY_COUNT):
        print("进程:%s 场次:%d" % (os.getpid(), i))
        data, winner = g.start_play()
        db.update_data(remove_lose_data(data, winner))
        gc.collect()


if __name__ == '__main__':
    pool = Pool(4)
    for i in range(5):
        pool.apply_async(start, ())
    pool.close()
    pool.join()
