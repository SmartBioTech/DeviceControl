from threading import Event

from core.data.manager import DataManager
from core.utils.time import now


class Command:

    def __init__(self, device_id, command_id: str, args: list, source: str, save_on_resolve=True):
        self.command_id = command_id
        self.args = args
        self.source = source
        self.device_id = device_id
        self.time_issued = now()

        self._resolved = Event()
        self.is_valid = None
        self.time_executed = None
        self.response = None
        self.save_on_resolve = save_on_resolve
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
        self.time_executed = now()
        self._resolved.set()
        if self.save_on_resolve:
            self.save_to_database()

    def save_to_database(self):
        if not self._saved:
            DataManager().save_cmd(self)
        self._saved = True

    def to_dict(self) -> dict:
        return {
            "time_issued": str(self.time_issued),
            "time_executed": str(self.time_executed),
            "device_id": str(self.device_id),
            "response": str(self.response),
            "target": str(self.args),
            "source": str(self.source),
            "command_id": str(self.command_id),
            "is_valid": int(self.is_valid)
        }
