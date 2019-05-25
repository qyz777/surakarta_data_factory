import sqlite3


class DBHelper(object):

    def __init__(self, db_name):
        self.__connect = sqlite3.connect(db_name)
        self.__connect.execute("PRAGMA synchronous = OFF")
        self.__cursor = self.__connect.cursor()

    def update_data(self, data):
        for info in data:
            table_name = "chess_num_" + str(info["chess_num"])
            where = {"board": info["board"],
                     "camp": info["camp"],
                     "from_x": info["from_x"],
                     "from_y": info["from_y"],
                     "to_x": info["to_x"],
                     "to_y": info["to_y"]}
            column = self.select(table_name, ["id", "prob"], where)
            if len(column) > 0:
                self._update(table_name, {"prob": int(column[0][1]) + 1}, {"id": int(column[0][0])})
            else:
                self._insert(table_name, info)

    def create_tables(self):
        for i in range(1, 25):
            table_name = "chess_num_" + str(i)
            sql = '''CREATE TABLE `{name}` (
                  `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                  `board` TEXT NOT NULL,
                  `camp` INTEGER NOT NULL,
                  `red_num` INTEGER NOT NULL,
                  `blue_num` INTEGER NOT NULL,
                  `chess_num` INTEGER NOT NULL,
                  `from_x` INTEGER NOT NULL,
                  `from_y` INTEGER NOT NULL,
                  `to_x` INTEGER NOT NULL,
                  `to_y` INTEGER NOT NULL,
                  `prob` INTEGER NOT NULL DEFAULT 0
            )'''.format(name=table_name)
            self.__connect.execute(sql)

    def _insert(self, table, data):
        keys = []
        values = []
        for key in data:
            keys.append(str(key))
            values.append("'{value}'".format(value=data[key]))
        sql = '''INSERT INTO {table} ({keys}) VALUES ({values})
        '''.format(table=table, keys=",".join(keys), values=",".join(values))
        self.__connect.execute(sql)

    def select(self, table, column, where=None):
        where_str = ""
        if len(where) > 0:
            where_list = []
            for key in where:
                item = "{key}='{value}'".format(key=key, value=where[key])
                where_list.append(item)
            where_str = " WHERE " + " and ".join(where_list)
        sql = '''SELECT {column} FROM {table} {where}
        '''.format(column=",".join(column), table=table, where=where_str)
        cursor = self.__connect.execute(sql)
        self.__connect.commit()
        return list(cursor)

    def _update(self, table, data, where=None):
        data_list = []
        for key in data:
            data_list.append("{key}='{value}'".format(key=key, value=data[key]))
        where_str = ""
        if len(where) > 0:
            where_list = []
            for key in where:
                item = "{key}='{value}'".format(key=key, value=where[key])
                where_list.append(item)
            where_str = " WHERE " + " and ".join(where_list)
        sql = '''UPDATE {table} SET {data} {where}
        '''.format(table=table, data=",".join(data_list), where=where_str)
        self.__connect.execute(sql)
