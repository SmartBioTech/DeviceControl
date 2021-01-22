from threading import Event

from . import app_manager
from .core.utils.time import now
from .models import Value
from .models import Event as DBevent


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
        self.time_executed = now()
        self._resolved.set()

    def save_command_to_db(self, event=1):
        if not self._saved:
            event = DBevent(dev_id=self.device_id, event_type=event, time=self.time_executed, args=self.args,
                            command=self.command_id, response=self.response)
            app_manager.dataManager.save_event(event)
        self._saved = True

    def save_data_to_db(self):
        if self.is_valid:
            channel = self.response.pop("channel", None)
            note = self.response.pop("outlier", None)
            for variable in self.response:
                value = Value(time=self.time_executed, value=self.response[variable], dev_id=self.device_id,
                              var_id=variable, channel=channel, note=note)
                app_manager.dataManager.save_value(value)
        else:
            event = DBevent(dev_id=self.device_id, event_type=2, time=self.time_executed, args=self.args,
                            command=self.command_id, response=self.response)
            app_manager.dataManager.save_event(event)

    def to_dict(self) -> dict:
        return {
            "time_issued": str(self.time_issued),
            "time_executed": str(self.time_executed),
            "device_id": str(self.device_id),
            "response": str(self.response),
            "arguments": str(self.args),
            "source": str(self.source),
            "command_id": str(self.command_id)
        }
