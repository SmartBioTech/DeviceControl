from abc import abstractmethod

from device_module.device import DeviceManager
from device_module.device_connector.abstract.device import Device
from utils.AbstractClass import Interface, abstractattribute


class BaseTask(metaclass=Interface):

    def __init__(self):
        self.is_active = True

    @abstractattribute
    def task_id(self):
        pass

    @abstractmethod
    def end(self):
        pass

    @abstractmethod
    def start(self):
        pass
