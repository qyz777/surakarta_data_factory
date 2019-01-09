from surakarta import game
from helper import db_helper
import os


PLAY_COUNT = 10

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
        db.update_data(game.start_play())

