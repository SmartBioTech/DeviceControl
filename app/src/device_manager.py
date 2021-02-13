from typing import Dict

from app.src.utils.abstract_device import Connector
from .utils.errors import IdError
from ..workspace.devices import classes


class DeviceManager:
    def __init__(self):
        self._devices: Dict[str, Connector] = {}

    def new_device(self, config: dict) -> Connector:
        device_class = config.get("device_class")
        device_type = config.get("device_type")
        if self._devices.get(config.get("device_id")) is not None:
            raise IdError("Connector with given ID already exists")
        device = self.load_class(device_class, device_type)(config)
        self._devices[device.device_id] = device
        return device

    def remove_device(self, device_id: str):
        device = self._devices.pop(device_id)
        device.end()

    def get_device(self, device_id: str) -> Connector:
        device = self._devices.get(device_id)
        if device is None:
            raise IdError("Connector with given ID: %s was not found" % device_id)
        return device

    def end(self):
        for key in list(self._devices.keys()):
            self.remove_device(key)

    def ping(self) -> Dict[str, bool]:
        result = {}

        for key, device in self._devices.items():
            result[key] = device.test_connection()

        return result

    @staticmethod
    def load_class(device_class: str, device_type: str) -> Connector.__class__:
        return classes[device_class][device_type]
