from abc import abstractmethod
from threading import Thread

from device_module.command import Command
from utils.AbstractClass import abstractattribute, Interface


class Device(metaclass=Interface):

    def __init__(self, config: dict):
        self.device_id = None
        self.device_class = None
        self.device_type = None
        self.address = None
        self.setup = {}

        self.__dict__.update(config)

        try:
            assert self.device_id is not None
            assert self.device_class is not None
            assert self.device_type is not None
            assert self.address is not None
        except AssertionError:
            raise AttributeError("Invalid configuration")

        # TODO: modify hw classes to accept config as a dict
        """
        self._physical_device = get_device_type_from_class(self.device_class,
                                                           self.device_class)(config)
        """
        self.is_alive = True
        self.is_queue_check_running = False
        self.queue = PriorityQueue()

    @abstractattribute
    def interpreter(self) -> dict:
        pass

    def __str__(self):
        return "{} @ {}".format(self.device_id, self.address)

    def __repr__(self):
        return "Device({}, {})".format(self.device_id, self.address)

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    def get_command_reference(self, cmd_id):
        command_reference = self.interpreter.get(cmd_id)
        if command_reference is None:
            raise AttributeError("Requested command ID is not defined in the device_module's Interpreter")
        return command_reference

    def get_capabilities(self):
        result = {}
        for key, func in self.interpreter.items():
            arguments = list(func.__code__.co_varnames)
            arguments.remove("self")
            result[key] = func.__name__, arguments
        return result

    def post_command(self, cmd: Command, priority=2):
        print("command accepted")
        self.queue.put(cmd, priority)
        if not self.is_queue_check_running:
            t = Thread(target=self.queue_new_item)
            t.start()

    def queue_new_item(self):
        self.is_queue_check_running = True
        print("queue check started")
        while self.queue.has_items():
            print("queue running")
            self.execute_command(self.queue.get())
        self.is_queue_check_running = False
        print("queue check stopped")

    def execute_command(self, command: Command):
        try:
            validity = True
            response = self.get_command_reference(command.command_id)(*command.args)
        except Exception as e:
            validity = False
            response = e

        command.response = response
        command.is_valid = validity
        command.executed_on = (self.device_type, self.device_id)
        command.resolved.set()

        return command

    def ping(self):
        cmd = Command(1, [], 'ping')
        self.post_command(cmd, priority=1)
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
