from surakarta import game
from helper import db_helper
import os
import gc


PLAY_COUNT = 10


def remove_lose_data(data_list, winner_camp):
    win_data = []
    for info in data_list:
        if info["camp"] == winner_camp:
            win_data.append(info)
    return win_data


if __name__ == '__main__':
    db = None
    if os.path.exists('./data.db'):
        db = db_helper.DBHelper("data.db")
    else:
        db = db_helper.DBHelper("data.db")
        db.create_tables()
    game = game.Game(is_debug=False)
    for i in range(0, PLAY_COUNT):
        print(i)
        data, winner = game.start_play()
        db.update_data(remove_lose_data(data, winner))
        gc.collect()

