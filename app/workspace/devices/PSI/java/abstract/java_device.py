from abc import abstractmethod
import jpype
import jpype.imports

from .. import Command, Connector, Log
from ..utils import controller


class JavaDevice(Connector):
    """
    Class to connect to Java-based devices and communicate with them.
    """
    def __init__(self, config, java_config_path):
        super(JavaDevice, self).__init__(config)
        self.controller = controller
        self.device = self.connect(java_config_path)
        self.interpreter = {}

    def connect(self, java_config_path):
        """
        Connect to CommanderConnector in JVM
        """
        if not self.controller.is_started:
            self.controller.start_controller()

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
        return super(JavaDevice, self).get_command_reference(cmd_id)

    def _execute_command(self, command: Command):
        """
        Method to execute given Command

        :param command: a Command to be executed
        :return: response from the command
        """
        try:
            validity = True
            response = self.controller.execute_command(self.get_command_reference(command.command_id), command.args)
        except Exception as e:
            validity = False
            response = e

        command.response = response
        command.is_valid = validity
        command.executed_on = (self.device_class, self.device_id)

        command.resolve()
        return command

