from abc import abstractmethod
from threading import Thread

from .workflow import Job, WorkflowProvider
from . import Log
from .AbstractClass import abstractattribute, Interface


class Connector(metaclass=Interface):
    def __init__(self, config: dict):
        self.setup = {}
        self.scheduler = WorkflowProvider().scheduler

        self.config = config
        self.__dict__.update(config)

        self.is_alive = True
        self._is_queue_check_running = False
        self._queue = PriorityQueue()

    def __eq__(self, other):
        return self.config == other.config

    def validate_attributes(self, required, class_name):
        for att in required:
            if att not in self.__dict__.keys():
                raise AttributeError("Connector {} must contain attribute {}".format(class_name, att))

    @abstractattribute
    def interpreter(self) -> dict:
        pass

    def __str__(self):
        return "Connector({})".format(self.__dict__)

    def __repr__(self):
        return str(self)

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

    def _post_command(self, cmd, priority=0):
        cmd.device_id = self.device_id
        job = Job(task=self._execute_command, args=[cmd])
        self.scheduler.schedule_job(job)

    def post_command(self, cmd, priority=2):
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

    def _execute_command(self, command):
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

        command.resolve()
        return command

    def end(self):
        self.is_alive = False
        self.disconnect()


class PriorityQueue:

    def __init__(self):
        self._items = []

    def put(self, command, priority: int):
        self._items.append((priority, command))
        self._items.sort(key=self._sort_by_priority)

    def get(self):
        return self._items.pop(0)[1]

    @staticmethod
    def _sort_by_priority(elem):
        return elem[0]

    def has_items(self):
        return len(self._items) != 0

    def __eq__(self, other):
        return self._items == other._items
