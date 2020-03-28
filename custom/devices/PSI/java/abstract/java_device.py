from abc import abstractmethod

import jpype
from custom.devices.PSI.java.utils.jvm_controller import is_jvm_started, start_jvm

import jpype.imports

from core.device.abstract import Connector


class JavaDevice(Connector):
    def __init__(self, config):
        super(JavaDevice, self).__init__(config)
        self.device = self.connect(self.address)
        self.interpreter = {}

    def connect(self, device_config):
        if not is_jvm_started():
            jpype.addClassPath('device_connector/java/lib/jar/bioreactor-commander-0.8.7.jar')
            start_jvm()

        commanderConnector = jpype.JClass("psi.bioreactor.commander.CommanderConnector")
        device = commanderConnector(device_config, self.address, 115200)

        serverPluginManager = jpype.JClass("psi.bioreactor.server.plugin.ServerPluginManager")
        serverPluginManager.getInstance().loadPlugins()
        device.connect(0)

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
