from helper import db_helper


class Energy:

    def __init__(self, ai_camp: int):
        self._ai_camp = ai_camp
        self._db = db_helper.DBHelper("data.db")

    def get_max_rate_step(self, camp: int, chess_num: int) -> (int, int, int, int):
        table_name = "chess_num_" + str(chess_num)
        data_list = self._db.select(table_name, ["*"], {"camp": camp})
        max_prob = -1
        max_index = 0
        index = 0
        for data in data_list:
            if data[9] > max_prob:
                max_prob = data[9]
                max_index = index
                break
            index += 1
        return data_list[max_index][6], data_list[max_index][7], data_list[max_index][8], data_list[max_index][9]

    def select_go(self, info: dict) -> list:
        table_name = "chess_num_" + str(info["chess_num"])
        where = {"board": info["board"], "camp": self._ai_camp}
        data = self._db.select(table_name, ["*"], where)
        max_index = 0
        max_value = 0
        if len(data) == 0:
            return []
        for i in range(0, len(data)):
            if data[i][9] > max_value:
                max_value = data[i][9]
                max_index = i
        return data[max_index]
