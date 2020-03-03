from threading import Thread
from typing import Dict

from device_module.device_connector.abstract.device import Device
from device_module.device_connector.hw_device_initializer import get_device_type_from_class
from device_module.command import Command
from utils.errors import IdError
from utils.singleton import singleton


@singleton
class DeviceManager:

    def __init__(self):
        self._devices: Dict[str, Device] = {}

    def new_device(self, config: dict) -> Device:
        device = get_device_type_from_class(config.get("device_class"), config.get("device_type"))(config)
        self._devices[device.device_id] = device
        return device

    def remove_device(self, device_id: str):
        device = self._devices.pop(device_id)
        try:
            device.disconnect()
        except AttributeError:
            raise IdError("Device with given ID was not found")

    def get_device(self, device_id: str) -> Device:
        return self._devices.get(device_id)
