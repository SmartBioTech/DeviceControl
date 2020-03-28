from abc import abstractmethod
from threading import Thread

from core.log import Log
from core.device.command import Command
from core.utils.AbstractClass import abstractattribute, Interface


class Connector(metaclass=Interface):

    def __init__(self, config: dict):
        self.device_id = None
        self.device_class = None
        self.address = None
        self.setup = {}

        self.__dict__.update(config)

        try:
            assert self.device_id is not None
            assert self.device_class is not None
            assert self.address is not None
        except AssertionError:
            raise AttributeError("Invalid configuration")

        # TODO: modify hw classes to accept config as a dict
        """
        self._physical_device = get_device_type_from_class(self.device_class,
                                                           self.device_class)(config)
        """
        self.is_alive = True
        self._is_queue_check_running = False
        self._queue = PriorityQueue()

    @abstractattribute
    def interpreter(self) -> dict:
        pass

    def __str__(self):
        return "{} @ {}".format(self.device_id, self.address)

    def __repr__(self):
        return "Connector({}, {})".format(self.device_id, self.address)

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    def get_command_reference(self, cmd_id):
        command_reference = self.interpreter.get(cmd_id)
        if command_reference is None:
            raise AttributeError("Requested command ID is not defined in the device's Interpreter")
        return command_reference

    def get_capabilities(self):
        result = {}
        for key, func in self.interpreter.items():
            arguments = list(func.__code__.co_varnames)
            arguments.remove("self")
            result[key] = func.__name__, arguments
        return result

    def post_command(self, cmd: Command, priority=2):
        cmd.device_id = self.device_id
        self._queue.put(cmd, priority)
        if not self._is_queue_check_running:
            t = Thread(target=self._queue_new_item)
            t.start()

    def _queue_new_item(self):
        self._is_queue_check_running = True
        while self._queue.has_items():
            self._execute_command(self._queue.get())
        self._is_queue_check_running = False

    def _execute_command(self, command: Command):
        try:
            validity = True
            response = self.get_command_reference(command.command_id)(*command.args)
        except Exception as e:
            validity = False
            response = e
            Log.error(e)

        command.response = response
        command.is_valid = validity
        command.executed_on = (self.device_class, self.device_id)

        if not command.is_awaited:
            command.save_to_database()

        command.resolve()

        return command

    def end(self):
        self.is_alive = False
        self.disconnect()


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
