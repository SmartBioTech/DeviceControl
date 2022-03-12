from typing import Dict

from app.src.utils.abstract_device import Connector
from .utils.errors import IdError, ClassError
from ..workspace.devices import classes


class DeviceManager:
    """
    Manages devices in the application.
    """
    def __init__(self):
        self._devices: Dict[str, Connector] = {}

    def new_device(self, config: dict) -> Connector:
        """
        Creates a new device in the application.

        Extra parameters:

        - 'device_id': string - ID of the device,
        - 'device_class': string - Class of the device,
        - 'device_type': string - Type of the device,
        - 'address': string - Address on which the connection to the device can be established,

        :param config: Configuration of the device with the specified extra parameters
        :return: the created device
        """
        device_class = config.get("device_class")
        device_type = config.get("device_type")
        if self._devices.get(config.get("device_id")) is not None:
            raise IdError("Connector with given ID already exists")
        try:
            device = self._load_class(device_class, device_type)(config)
        except KeyError:
            raise ClassError("Unknown device class/type: {}/{}".format(device_class, device_type))
        self._devices[device.device_id] = device
        return device

    def remove_device(self, device_id: str):
        """
        Terminates an existing device.

        :param device_id: ID of the device
        """
        device = self._devices.pop(device_id)
        device.end()

    def get_device(self, device_id: str) -> Connector:
        """
        Get an existing device reference.

        :param device_id: ID of the device
        :return: the requested device
        """
        device = self._devices.get(device_id)
        if device is None:
            raise IdError("Connector with given ID: %s was not found" % device_id)
        return device

    def end(self):
        """
        Terminates all existing devices.
        """
        for key in list(self._devices.keys()):
            self.remove_device(key)

    def ping(self) -> Dict[str, bool]:
        """
        Tests connectivity with each existing device.

        :return: A dictionary {"device_id": true/false}
        """
        result = {}

        for key, device in self._devices.items():
            result[key] = device.test_connection()

        return result

    @staticmethod
    def _load_class(device_class: str, device_type: str) -> Connector.__class__:
        return classes[device_class][device_type]
