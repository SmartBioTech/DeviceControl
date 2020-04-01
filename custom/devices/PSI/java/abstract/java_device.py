import threading
from abc import abstractmethod

import jpype
from custom.devices.PSI.java.utils import Controller

import jpype.imports

from core.device.abstract import Connector


class JavaDevice(Connector):
    def __init__(self, config, java_config_path):
        super(JavaDevice, self).__init__(config)
        self.device = self.connect(java_config_path)
        self.interpreter = {}

    def connect(self, java_config_path):
        Controller.start_jvm()
        if not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()

        device = Controller.commander_connector(java_config_path, self.address, 115200)

        threading.Thread(target=device.connect, args=[0]).start()
        return device

    def disconnect(self):
        self.device.disconnect()

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    def get_command_reference(self, cmd_id):
        if not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()
        return super(JavaDevice, self).get_command_reference(cmd_id)
