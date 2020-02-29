from typing import Dict

from device_module.device import Device


class Node:

    def __init__(self):
        self._devices: Dict[str, Device] = {}

    def get_by_id(self, device_id: str):
        self._devices.get(device_id)

    def get_all_of_type(self, requested_type: str, target_dict=None):
        if target_dict is None:
            target_dict = self._devices

        result = {}
        for key, device in target_dict.items():
            if device.device_type == requested_type:
                result.update({key: device})
        return result

    def get_all_of_class(self, requested_class: str, target_dict=None):
        if target_dict is None:
            target_dict = self._devices

        result = {}
        for key, device in target_dict.items():
            if device.device_class == requested_class:
                result.update({key: device})

    def get_all_of_class_and_type(self, requested_class, requested_type, target_dict=None):
        if target_dict is None:
            target_dict = self._devices

        return self.get_all_of_class(requested_class,
                                     self.get_all_of_type(requested_type,
                                                          target_dict)
                                     )

    def add_device(self, device: Device):
        self._devices.update({device.device_id, device})
