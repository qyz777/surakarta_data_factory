from surakarta import game
from helper import db_helper
import os, time
from multiprocessing import Queue, Process


PLAY_COUNT = 2


def remove_lose_data(data_list, winner_camp):
    win_data = []
    for info in data_list:
        if info["camp"] == winner_camp:
            win_data.append(info)
    return win_data


def start(q: Queue):
    g = game.Game(is_debug=False)
    for i in range(0, PLAY_COUNT):
        print("进程:%s 场次:%d" % (os.getpid(), i))
        data, winner = g.start_play()
        q.put(remove_lose_data(data, winner))


def write_into_db(q: Queue):
    db = db_helper.DBHelper("data.db")
    while True:
        data = q.get()
        s = time.time()
        db.update_data(data)
        e = time.time()
        print("数量:%d 耗时:%ss" % (len(data), e - s))


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
