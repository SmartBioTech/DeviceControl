from threading import Thread
from typing import Optional

from core.data.dao import Dao
from core.utils.db import enquote
from core.utils.singleton import singleton


@singleton
class DataManager:
    def __init__(self, ws_client=None):
        self.last_seen_id = {'values': {}, 'events': {}}
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

    def update_experiment(self, device_id):
        pass

    def save_variable(self):
        # TODO: add also an event about creating a new variable
        pass

    def _get_data(self, conditions, device_id, table):
        response = Dao.select(table, conditions)
        result = {}

        columns = list.copy(Dao.tables['table'])

        for row in response:
            log_id = int(row[0])
            row = dict(zip(columns, (row[1:])))
            for key, item in row.items():
                # noinspection PyBroadException
                try:
                    item = eval(item)
                    row[key] = item
                except Exception:
                    continue
            result[log_id] = row

        if device_id is not None and response:
            self.last_seen[table][device_id] = max(result.keys())

        return result

    def get_data(self,
                 log_id: Optional[int] = None,
                 last_time: Optional[str] = None,
                 device_id: Optional[str] = None,
                 data_type: str = 'values'):

        where_conditions = []
        if device_id is not None:
            where_conditions.append("device_id={}".format(enquote(device_id)))

        if last_time is not None:
            where_conditions.append("TIMESTAMP(time)>TIMESTAMP({})".format(last_time))
        else:
            if log_id is None:
                log_id = self.last_seen_id[data_type].get(device_id, 0)
            where_conditions.append("id>{}".format(log_id))

        return self._get_data(where_conditions, device_id, data_type)

    def get_latest_data(self, device_id, data_type: str = 'values'):
        where_conditions = []
        if device_id is None:
            where_conditions.append("log_id=(SELECT MAX(id) FROM {})".format(data_type))
        else:
            where_conditions.append(
                "log_id=(SELECT MAX(id) FROM {} WHERE device_id={})".format(data_type, enquote(device_id)),
            )
        return self._get_data(where_conditions, device_id, data_type)
