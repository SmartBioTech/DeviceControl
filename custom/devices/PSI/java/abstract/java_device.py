import threading
from abc import abstractmethod

import jpype
import jpype.imports

from core.device.abstract import Connector
from custom.devices.PSI.java.utils import Controller


class JavaDevice(Connector):
    def __init__(self, config, java_config_path):
        super(JavaDevice, self).__init__(config)
        self.device = self.connect(java_config_path)
        self.interpreter = {}

    def connect(self, java_config_path):
        Controller.start_jvm()
        if not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()

        commander_connector = jpype.JClass("psi.bioreactor.commander.CommanderConnector")

        device = commander_connector(java_config_path, self.address, 115200)

        Controller.load_plugins()

        device.connect(0)
        return device

    def disconnect(self):
        self.device.disconnect()

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    def get_command_reference(self, cmd_id):
        print("JAVA SPECIFIC COMMAND REFERENCE GETTER CALLED")
        if not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()
            print("JAVA: THREAD ATTACHED TO JVM")

        return super(JavaDevice, self).get_command_reference(cmd_id)
