from multiprocessing.context import Process
from threading import Thread, Event
from time import sleep

from device_connector.hw_device_initializer import get_device_type_from_class
from device_module.command import Command
from device_module.configuration import DeviceConfig


class Device:

    def __init__(self, config: dict):
        self.device_id = None
        self.device_class = None
        self.device_type = None

        self.__dict__.update(config)

        try:
            assert self.device_id is not None
            assert self.device_class is not None
            assert self.device_type is not None
        except AssertionError:
            raise AttributeError("Invalid configuration")

        # TODO: modify hw classes to accept config as a dict
        self._physical_device = get_device_type_from_class(self.device_class,
                                                           self.device_class)(config)
        self.is_alive = True
        self.is_queue_check_running = False
        self.queue = PriorityQueue()

    def add_command(self, cmd: Command, priority=2):
        print("command accepted")
        self.queue.put(cmd, priority)
        if not self.is_queue_check_running:
            p = Thread(target=self.queue_new_item)
            p.start()

    def queue_new_item(self):
        self.is_queue_check_running = True
        while self.queue.has_items():
            self.execute_command(self.queue.get())
        self.is_queue_check_running = False

    def execute_command(self, command: Command):
        try:
            validity = True
            response = self._physical_device.get_command_reference(command.command_id)(*command.args)
        except Exception as e:
            validity = False
            response = e

        command.response = response
        command.is_valid = validity
        command.executed_on = (self.device_type, self.device_id)

        return command

    def disconnect(self):
        self.is_alive = False
        while self.queue.has_items():
            self.queue.get()
        self._physical_device.disconnect()

    def ping(self):
        cmd = Command(1, [], 'ping')
        self.add_command(cmd, priority=1)
        cmd.resolved.wait()
        return cmd.is_valid


class PriorityQueue:

    def __init__(self):
        self._items = []

    def put(self, command: Command, priority: int):
        self._items.append((priority, command))
        self._items.sort(key=self._sort_by_priority)

    def get(self):
        return self._items.pop(0)[1]

    @staticmethod
    def _sort_by_priority(elem):
        return elem[0]

    def has_items(self):
        return len(self._items) != 0
