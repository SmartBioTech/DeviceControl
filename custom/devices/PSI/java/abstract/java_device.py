import threading
from abc import abstractmethod

import jpype
import jpype.imports

from core.data.command import Command
from core.device.abstract import Connector
from core.log import Log
from custom.devices.PSI.java.utils.jvm_controller import Controller


class JavaDevice(Connector):
    def __init__(self, config, java_config_path):
        super(JavaDevice, self).__init__(config)
        self.controller = Controller()
        self.device = self.connect(java_config_path)
        self.interpreter = {}

    def connect(self, java_config_path):
        def _connect(path):
            if not jpype.isThreadAttachedToJVM():
                jpype.attachThreadToJVM()

            commander_connector = jpype.JClass("psi.bioreactor.commander.CommanderConnector")

            device = commander_connector(path, self.address, 115200)

            self.controller.load_plugins()

            device.connect(0)
            return device
        return self.controller.execute_command(_connect, [java_config_path])

    def disconnect(self):
        self.device.disconnect()

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    def get_command_reference(self, cmd_id):
        print("JAVA SPECIFIC COMMAND REFERENCE GETTER CALLED")

        return super(JavaDevice, self).get_command_reference(cmd_id)

    def _execute_command(self, command: Command):
        try:
            validity = True
            response = self.controller.execute_command(self.get_command_reference(command.command_id), command.args)
        except Exception as e:
            validity = False
            response = e
            Log.error(e)

        command.response = response
        command.is_valid = validity
        command.executed_on = (self.device_class, self.device_id)

        command.resolve()
        return command

