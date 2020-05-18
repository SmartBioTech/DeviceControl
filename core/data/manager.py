from threading import Thread
from typing import Optional

from core.data.dao import Dao
from core.utils.db import enquote
from core.utils.singleton import singleton


@singleton
class DataManager:
    def __init__(self, ws_client=None):
        self.last_seen = {}
        self.ws_client = ws_client

    def save_cmd(self, cmd):
        Dao.insert(Dao.cmd_table, [
            ("time_issued", str(cmd.time_issued)),
            ("time_executed", str(cmd.time_executed)),
            ("device_id", str(cmd.device_id)),
            ("response", str(cmd.response)),
            ("target", str(cmd.args)),
            ("source", str(cmd.source)),
            ("command_id", str(cmd.command_id)),
            ("is_valid", int(cmd.is_valid))
        ]
                   )

        if self.ws_client is not None:
            Thread(target=self.ws_client.send_data, args=[cmd.to_dict()]).start()

    def _get_data(self, conditions, device_id):
        response = Dao.select(Dao.cmd_table, Dao.cmd_table_columns, conditions)
        result = {}

        columns = list.copy(Dao.cmd_table_columns)

        columns.pop(0)

        for row in response:
            log_id = row[0]
            row = row[1:]
            result[log_id] = row

        if device_id is not None and response:
            self.last_seen[device_id] = max(result.keys())

        return result

    def get_data(self,
                 log_id: Optional[int] = None,
                 time: Optional[str] = None,
                 device_id: Optional[str] = None):

        where_conditions = []
        if device_id is not None:
            where_conditions.append(f"device_id={enquote(device_id)}")

        if time is not None:
            where_conditions.append(f"TIMESTAMP(time_issued)>TIMESTAMP({time})")

        elif log_id is not None:
            where_conditions.append(f"log_id>{log_id}")

        else:
            log_id = self.last_seen.get(device_id, 0)
            where_conditions.append(f"log_id>{log_id}")

        return self._get_data(where_conditions, device_id)

    def get_latest_data(self, device_id):
        where_conditions = []
        if device_id is None:
            where_conditions.append(
                f"log_id=(SELECT MAX(log_id) FROM {Dao.cmd_table})"
            )
        else:
            where_conditions.append(
                f"log_id=(SELECT MAX(log_id) FROM {Dao.cmd_table} WHERE device_id={enquote(device_id)})",
            )
        return self._get_data(where_conditions, device_id)
