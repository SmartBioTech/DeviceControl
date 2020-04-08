from threading import Event

from core.data.manager import DataManager
from core.utils.TimeStamper import now


class Command:

    def __init__(self, device_id, command_id: str, args: list, source: str, is_awaited=False):
        self.command_id = command_id
        self.args = args
        self.source = source
        self.device_id = device_id
        self.time_issued = now()

        self._resolved = Event()
        self.is_valid = None
        self.time_executed = None
        self.response = None
        self.is_awaited = is_awaited
        self._saved = False

    def __str__(self):
        return "SOURCE:{} DEVICE: {} ID: {},  IS VALID: {}  RESPONSE: {}".format(
            self.source,
            self.device_id,
            self.command_id,
            self.is_valid,
            self.response
        )

    def await_cmd(self, timeout=None) -> bool:
        return self._resolved.wait(timeout=timeout)

    def resolve(self):
        self._resolved.set()

    def save_to_database(self):
        if not self._saved:
            DataManager().save_cmd(self)
        self._saved = True
