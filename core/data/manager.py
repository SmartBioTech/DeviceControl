from typing import Optional

from core.data.dao import Dao
from core.utils.db import enquote_all, enquote
from core.utils.singleton import singleton


@singleton
class DataManager:
    def __init__(self):
        self.last_seen = {}

    def save_cmd(self, cmd):
        Dao.insert(Dao.cmd_table, [
            ("time_issued", str(cmd.time_issued)),
            ("time_executed", str(cmd.time_executed)),
            ("device_id", str(cmd.device_id)),
            ("response", str(cmd.response)),
            ("target", str(cmd.args)),
            ("source", str(cmd.source)),
            ("command_id", str(cmd.command_id))
        ]
                   )

    def get_data_by_id(self, log_id: Optional[int] = None, device_id: Optional[str] = None):
        where_conditions = []
        if device_id is not None:
            device_id = enquote(device_id)
            where_conditions.append(f"device_id={device_id}")

            if log_id is None:
                log_id = self.last_seen.get(device_id, 0)

            where_conditions.append(f"log_id>{log_id}")

        elif log_id is not None:
            where_conditions.append(f"log_id>{log_id}")

        response = Dao.select(Dao.cmd_table, Dao.cmd_table_columns, where_conditions)
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
