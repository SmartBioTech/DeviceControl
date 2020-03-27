from typing import Dict

from core.device_module.device_connector.abstract.device import Device
from core.utils.errors import IdError
from core.utils.singleton import singleton
from custom.devices import classes


@singleton
class DeviceManager:

    def __init__(self):
        self._devices: Dict[str, Device] = {}

    def new_device(self, config: dict) -> Device:
        if self._devices.get(config.get("device_id")) is not None:
            raise IdError("Device with given ID already exists")
        device = self.load_class(config.get("device_class"))(config)
        self._devices[device.device_id] = device
        return device

    def remove_device(self, device_id: str):
        device = self._devices.pop(device_id)
        device.disconnect()

    def get_device(self, device_id: str) -> Device:
        device = self._devices.get(device_id)
        if device is None:
            raise IdError("Device with given ID: %s was not found" % device_id)
        return device

    def end(self):
        for name, device in self._devices.items():
            device.end()

    def ping(self) -> Dict[str, bool]:
        result = {}

        for key, device in self._devices.items():
            result[key] = device.ping()

        return result

    @staticmethod
    def load_class(class_id: str) -> Device.__class__:
        return classes.get(class_id)
