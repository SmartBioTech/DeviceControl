from queue import PriorityQueue
from threading import Thread, Event

from device_connector.hw_device_initializer import get_class
from device_module.command import Command
from device_module.configuration import DeviceConfig


class Device:

    def __init__(self, config: DeviceConfig):
        self.config = config

        try:
            self.device_class_name = self.config.device_class
            self.device_type_name = self.config.device_type
            self.device_id = self.config.device_id
        except AttributeError:
            raise AttributeError("Invalid configuration")

        self.physicalDevice = get_class(self.device_class_name,
                                        self.device_type_name)(self.config)

        self.is_alive = True
        self.queue = QueueOfCommands(self)
        self.queue.start()

    def add_command(self, cmd: Command):
        self.queue.add_command(cmd)

    def execute_command(self, command: Command):
        try:
            validity = True
            response = self.physicalDevice.get_command_reference(command.command_id)(*command.args)
        except Exception as e:
            validity = False
            response = e

        command.response = response
        command.is_valid = validity
        command.executed_on = (self.device_type_name, self.device_id)

        return command

    def disconnect(self):
        self.is_alive = False
        while not self.queue.empty():
            self.queue.get()
        self.physicalDevice.disconnect()

    def ping(self):
        cmd = Command(1, [], 'ping')
        self.queue.add_command(cmd, priority=1)
        cmd.resolved.wait()
        return cmd.is_valid


class QueueOfCommands(Thread, PriorityQueue):

    def __init__(self, device: Device):
        PriorityQueue.__init__(self)
        Thread.__init__(self)
        self.name = "{}/{}/queue_thread".format(device.device_type_name,
                                                device.device_id)
        self.flag = Event()
        self.device = device

    def add_command(self, command: Command, priority: int = 2):
        self.put((priority, command))
        self.flag.set()

    def run(self):
        while self.device.is_alive:
            self.flag.wait()
            while not self.empty():
                cmd = self.device.execute_command(self.get()[1])
                cmd.resolved.set()
            self.flag.clear()
