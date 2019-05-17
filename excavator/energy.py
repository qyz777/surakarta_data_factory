from helper import db_helper


class Energy:

    def __init__(self):
        self.db = db_helper.DBHelper("data.db")

    def show_win_rate(self):
        for i in range(1, 25):
            table_name = "chess_num_" + str(i)
            data_list = self.db.select(table_name, ["*"], {"camp": 1})
            prob_sum = 0
            print("————————{table_name}————————".format(table_name=table_name))
            for row in data_list:
                prob_sum += row[10] + 1
            for row in data_list:
                print("{from_x},{from_y}:{to_x},{to_y} -> 胜率:{win}".format(from_x=row[6],
                                                                           from_y=row[7],
                                                                           to_x=row[8],
                                                                           to_y=row[9],
                                                                           win=(row[10] + 1) / prob_sum))

    def get_max_rate_step(self, camp: int, chess_num: int) -> (int, int, int, int):
        table_name = "chess_num_" + str(chess_num)
        data_list = self.db.select(table_name, ["*"], {"camp": camp})
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
