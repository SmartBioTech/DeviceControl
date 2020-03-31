import threading
from abc import abstractmethod

import jpype
from custom.devices.PSI.java.utils.jvm_controller import is_jvm_started, start_jvm

import jpype.imports

from core.device.abstract import Connector


class JavaDevice(Connector):
    def __init__(self, config, java_config_path):
        super(JavaDevice, self).__init__(config)
        self.device = self.connect(java_config_path)
        self.interpreter = {}

    def connect(self, java_config_path):
        if not is_jvm_started():
            jpype.addClassPath('custom/devices/PSI/java/lib/jar/bioreactor-commander-0.8.7.jar')
            start_jvm()

        commander_connector = jpype.JClass("psi.bioreactor.commander.CommanderConnector")
        device = commander_connector(java_config_path, self.address, 115200)

        server_plugin_manager = jpype.JClass("psi.bioreactor.server.plugin.ServerPluginManager")
        server_plugin_manager.getInstance().loadPlugins()
        
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
