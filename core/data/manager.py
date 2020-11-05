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

        self.variables = []  # TODO: get all variable names from DB

    def save_value(self, values):
        if values[3] not in self.variables:
            # TODO: add variable ( send also dev_id)
            pass
        Dao.insert('values', values)

    def save_event(self, values):
        Dao.insert('events', values)

    def save_device(self, device):
        # TODO: store device if does not exists
        #  + store experiment (temporal hack) !!!
        pass

    def save_experiment(self):
        # TODO: use utils.now()
        pass

    def save_variable(self):
        # TODO: add also an event about creating a new variable
        pass

    # TODO: add argument for event/value data type
    def _get_data(self, conditions, device_id):
        response = Dao.select(Dao.cmd_table, Dao.cmd_table_columns, conditions)
        result = {}

        columns = list.copy(Dao.cmd_table_columns)

        columns.pop(0)

        for row in response:
            log_id = int(row[0])
            row = dict(zip(Dao.cmd_table_columns[1:], (row[1:])))
            for key, item in row.items():
                # noinspection PyBroadException
                try:
                    item = eval(item)
                    row[key] = item
                except Exception:
                    continue
            result[log_id] = row

        if device_id is not None and response:
            self.last_seen[device_id] = max(result.keys())

        return result

    # TODO: add argument for event/value data type
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

    # TODO: add argument for event/value data type
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
