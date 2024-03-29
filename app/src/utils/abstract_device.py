import sys
from abc import abstractmethod
from threading import Thread

from .workflow import Job, WorkflowProvider
from . import Log
from .AbstractClass import abstractattribute, Interface


class Connector(metaclass=Interface):
    """
    An interface which every implemented Device must implement.
    For additional information, see Wiki_.

    .. _Wiki: https://github.com/SmartBioTech/DeviceControl/wiki/New-device
    """
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
        """
        A dictionary with the defined commands {command_id: command_reference}
        """
        pass

    def __str__(self):
        return "Connector({})".format(self.__dict__)

    def __repr__(self):
        return str(self)

    @abstractmethod
    def disconnect(self) -> None:
        """
        Terminate the connection between the application and physical device.
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test the connection between the application and physical device.
        """
        pass

    def get_command_reference(self, cmd_id):
        """
        Get the command reference by its ID.

        :param cmd_id: ID of the command
        :return: command reference
        """
        command_reference = self.interpreter.get(cmd_id)
        if command_reference is None:
            raise AttributeError("Requested command ID is not defined in the device's Interpreter")
        return command_reference

    def get_capabilities(self) -> dict:
        """
        Retrieves information about the commands that the implemented device can execute.

        :return: dictionary {command_id: (function_name, arguments)}
        """
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
        """
        Queues a command for execution.

        :param cmd:
        :param priority: Priority in which the orders will execute.
                         Commands with same priority will exeute in the order they were queued for execution.
        """
        cmd.device_id = self.device_id
        self._queue.put(cmd, priority)
        if not self._is_queue_check_running:
            t = Thread(target=self._queue_new_item)
            t.start()

    def post_manual_command(self, cmd, priority=0):
        """
        Queues a command for execution and waits until it has been executed.

        :param cmd: command object
        :param priority: priority the command should take over other commands
        """
        cmd.device_id = self.device_id
        self._queue.put(cmd, priority)
        if not self._is_queue_check_running:
            t = Thread(target=self._queue_new_item)
            t.start()
        cmd.await_cmd()
        cmd.save_command_to_db()

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

        command.response = response
        command.is_valid = validity
        command.executed_on = (self.device_class, self.device_id)

        command.resolve()
        return command

    def end(self):
        """
        Terminates the device.
        """
        self.scheduler.is_active = False
        self.is_alive = False
        self.disconnect()

    def whoami(self):
        """
        Identify name of calling function

        :return: name of calling function
        """
        return sys._getframe(1).f_code.co_name

    def _raise_error(self, function, message):
        raise Exception(function + ": " + str(message))


class PriorityQueue:
    """
    A queue in which items are processed on an order based on their priority.
    """
    def __init__(self):
        self._items = []

    def put(self, command, priority: int):
        """
        Put a command into the queue.

        :param command: command object
        :param priority: priority the command should take over other commands
        """
        self._items.append((priority, command))
        self._items.sort(key=self._sort_by_priority)

    def get(self):
        """
        Gets an element from the front of the queue.
        """
        return self._items.pop(0)[1]

    @staticmethod
    def _sort_by_priority(elem):
        return elem[0]

    def has_items(self):
        """
        Checks if the queue is empty or not.

        :return: False if empty, true if not.
        """
        return len(self._items) != 0

    def __eq__(self, other):
        return self._items == other._items
