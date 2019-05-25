import os
import time
from multiprocessing import Queue, Process

from helper.db_helper import DBHelper
from surakarta import game

PLAY_COUNT = 100


def remove_lose_data(data_list, winner_camp):
    win_data = []
    for info in data_list:
        if info["camp"] == winner_camp:
            win_data.append(info)
    return win_data


def start(q: Queue):
    g = game.Game(is_debug=False, camp=-1)
    for i in range(0, PLAY_COUNT):
        print("进程:%s 场次:%d" % (os.getpid(), i))
        data, winner = g.start_play()
        q.put(remove_lose_data(data, winner))


def write_into_db(q: Queue):
    if os.path.exists('./data.db'):
        db = DBHelper("data.db")
    else:
        db = DBHelper("data.db")
        db.create_tables()
    while True:
        data = q.get()
        s = time.time()
        db.update_data(data)
        e = time.time()
        print("数量:%d 耗时:%.2fs" % (len(data), e - s))


if __name__ == '__main__':
    q = Queue()
    process_db = Process(target=write_into_db, args=(q, ))
    process_db.start()
    process_gen_1 = Process(target=start, args=(q, ))
    process_gen_2 = Process(target=start, args=(q, ))
    process_gen_1.start()
    process_gen_2.start()
    process_gen_1.join()
    process_gen_2.join()
    process_db.terminate()
