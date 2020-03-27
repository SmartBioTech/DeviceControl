import mysql.connector as cn

from core.utils.singleton import singleton


@singleton
class DatabaseManager:

    def __init__(self):
        self.USER = "DeviceControl"
        self.DATABASE = "device_control"
        self.HOST = "127.0.0.1"
        self.PASSWORD = "&Bioarineo1"
        self.device_unseen = {}
        self.create_table()  # initialize the table

    def connect(self):
        """
        Establish connection to the database.
        :return: mysql.connector.connect object
        """
        return cn.connect(host=self.HOST,
                          user=self.USER,
                          password=self.PASSWORD,
                          db=self.DATABASE)

    def create_table(self):
        """
        Create the save_to_database table
        :return: None
        """
        con = self.connect()
        cursor = con.cursor()

        cursor.execute(("CREATE TABLE IF NOT EXISTS executed_commands ("
                        "log_id int NOT NULL auto_increment,"
                        "time_issued VARCHAR(255),"
                        "device_id VARCHAR(255),"
                        "command_id VARCHAR(255),"
                        "target VARCHAR(255),"
                        "response VARCHAR(1000),"
                        "time_executed VARCHAR(255),"
                        "source VARCHAR(255), "
                        "PRIMARY KEY (log_id))"))

        con.commit()

        cursor.close()
        con.close()

    def drop_table(self):
        con = self.connect()
        cursor = con.cursor()
        cursor.execute("DROP TABLE %s" % self.TABLE)
        con.commit()

    def get_for_system(self, device_id, time):
        """
        Getter - retrieves data from save_to_database and remembers which data have been shown in the current session. Already seen
        data will not be loaded in the next get.
        :param device_id: device_id to search for
        :param time: time from which to begin the search
        :return: list of the table's rows
        """
        con = self.connect()
        cursor = con.cursor()
        if device_id not in self.device_unseen:
            self.device_unseen[device_id] = [0, "'0000-00-00 00:00:00'"]

        if time is not None:
            self.device_unseen[device_id] = [0, time]

        select = ('SELECT * FROM executed_commands WHERE ('
                  'log_id > %s AND '
                  'device_id = %s AND '
                  'TIMESTAMP(time_issued) >= TIMESTAMP(%s)) '
                  'ORDER BY log_id' % (self.device_unseen[device_id][0], device_id, self.device_unseen[device_id][1]))

        cursor.execute(select)
        rows = cursor.fetchall()
        cursor.close()
        con.close()

        if rows:
            self.device_unseen[device_id][0] = rows[-1][0]

        return rows

    def update_log(self, cmd):
        """
        Is called by executioner - saves data(responses) to the save_to_database table.
        :param cmd:
        :return: None
        """
        con = self.connect()
        cursor = con.cursor()

        query = ("INSERT INTO executed_commands "
                 "(time_issued, device_id, command_id, target, response, time_executed, source)"
                 "VALUES (%s, %s, %s, %s, %s, %s, %s)")

        query_args = (
            str(cmd.time_issued),
            str(cmd.device_id),
            str(cmd.command_id),
            str(cmd.args),
            str(cmd.response),
            str(cmd.time_executed),
            str(cmd.source)
        )

        cursor.execute(query, query_args)
        print("Updating database: " + str(cmd))
        con.commit()
        cursor.close()
        con.close()
