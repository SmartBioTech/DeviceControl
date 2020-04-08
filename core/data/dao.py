from typing import List, Optional, Tuple

import mysql.connector as cn

from core.utils.singleton import singleton


@singleton
class Dao:

    def __init__(self, user: str = None, database: str = None, host: str = None, password: str = None):
        self._user = user if user is not None else "DeviceControl"
        self._database = database if database is not None else "device_control"
        self._host = host if host is not None else "127.0.0.1"
        self._password = password if password is not None else "&Bioarineo1"

        self.cmd_table = "executed_commands"
        self.cmd_table_columns: list = [
            "log_id",
            "time_issued",
            "device_id",
            "command_id",
            "target",
            "response",
            "time_executed",
            "source"
        ]
        self._create_table()  # initialize the table

    def _connect(self):
        """
        Establish connection to the database.
        :return: mysql.connector.connect object
        """
        return cn.connect(host=self._host,
                          user=self._user,
                          password=self._password,
                          db=self._database)

    def _create_table(self):
        """
        Create the save_to_database table
        :return: None
        """
        query = (f"CREATE TABLE IF NOT EXISTS {self.cmd_table} ("
                 "log_id int NOT NULL auto_increment,"
                 "time_issued VARCHAR(255),"
                 "device_id VARCHAR(255),"
                 "command_id VARCHAR(255),"
                 "target VARCHAR(255),"
                 "response VARCHAR(1000),"
                 "time_executed VARCHAR(255),"
                 "source VARCHAR(255), "
                 "PRIMARY KEY (log_id))")

        self._execute_query(query)

    def _execute_query(self, query):
        con = self._connect()
        cursor = con.cursor()
        cursor.execute(query)
        try:
            result = cursor.fetchall()
        except cn.errors.InterfaceError:
            result = None

        con.commit()
        cursor.close()
        con.close()

        return result

    def select_all(self, table: str) -> str:
        query = "SELECT * FROM {}".format(table)

        return self._execute_query(query)

    def select(self, table: str, columns: List[str], where: Optional[List[str]] = None) -> str:

        if where:
            where = " WHERE " + ", ".join(where)
        else:
            where = ""

        query = "SELECT %s FROM %s%s" % (", ".join(columns), table, where)

        return self._execute_query(query)

    def insert(self, table: str, column_value_pairs: List[Tuple[str, str]]):

        columns = []
        values = []

        for pair in column_value_pairs:
            columns.append(pair[0])
            values.append(pair[1])

        for i in (range(len(values))):
            values[i] = f"\"{values[i]}\""

        columns = ", ".join(columns)
        values = ", ".join(values)

        query = f"""INSERT INTO {table} ({columns}) VALUES ({values})"""

        self._execute_query(query)

    def _drop(self, table: str):
        query = f"DROP TABLE {table}"
        self._execute_query(query)


Dao = Dao()
