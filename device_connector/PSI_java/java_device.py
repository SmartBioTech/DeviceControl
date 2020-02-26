import jpype
from device_connector.PSI_java import jvm_controller

import jpype.imports

from device_connector.abstract.device import Device


class JavaDevice(Device):
    def __init__(self, device_id, address, path):
        self.id = device_id
        self.address = address
        self.device = self.connect(path)
        self.interpreter = {}

    def connect(self, device_config):
        if not jvm_controller.isJVMStarted():
            jpype.addClassPath('device_connector/PSI_java/lib/jar/bioreactor-commander-0.8.7.jar')
            jvm_controller.startJVM()

        CommanderConnector = jpype.JClass("psi.bioreactor.commander.CommanderConnector")
        device = CommanderConnector(device_config, self.address, 115200)

        ServerPluginManager = jpype.JClass("psi.bioreactor.server.plugin.ServerPluginManager")
        ServerPluginManager.getInstance().loadPlugins()
        device.connect(0)

        return device

    def disconnect(self):
        self.device.disconnect()

    def __str__(self):
        return self.id + " @ " + str(self.address)

    def __repr__(self):
        return "Device(" + self.id + ", " + str(self.address) + ")"
