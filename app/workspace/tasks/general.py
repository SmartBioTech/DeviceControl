from math import gcd
from functools import reduce
from threading import Thread, Event
from time import sleep

from .. import Command, BaseTask
from ... import app_manager


class MeasureAllDesync(BaseTask):
    """
    Asynchronous periodical measurement of chosen variables.

    It is necessary to provide a dictionary, where for each time period particular variables are given
      'frequency_to_commands': {time_period_1: {"variable_X": command_X, "variable_Y": command_Y, ...},
                                time_period_2: {"variable_Z": command_Z, "variable_W": command_W, ...},
                                ...}

    Additional extra parameters:
    'device_id': str - ID of target device
    """
    def __init__(self, config):
        self.frequency_to_commands = {}
        self.device_id: str = ""
        self.od_task_id: str = ""

        self.__dict__.update(config)
        super(MeasureAllDesync, self).__init__(config)

        self.device = app_manager.deviceManager.get_device(self.device_id)
        self.active = True

        self.counters_to_commands, self.sleep_time = self.find_gcd_counters(self.frequency_to_commands)

    def start(self):
        t = Thread(target=self._run)
        t.start()

    def _run(self):
        current_time = 0
        while self.active:
            for counter, commands in self.counters_to_commands.items():
                if current_time % counter == 0:
                    self.execute_commands(commands)
            sleep(self.sleep_time)
            current_time += self.sleep_time

    def find_gcd_counters(self, frequency_to_commands):
        value = reduce(gcd, list(map(int, frequency_to_commands.keys())))
        frequency_to_commands = {int(frequency)//value: frequency_to_commands[frequency]
                                 for frequency in frequency_to_commands.keys()}
        return frequency_to_commands, value

    def execute_commands(self, commands):
        executed_commands = []
        for _name, _command in commands.items():
            command = Command(self.device_id,
                              _command.get("id"),
                              _command.get("args", []),
                              self.task_id,
                              is_awaited=True)
            executed_commands.append((_name, command))
            self.device.post_command(command, 1)

        for name, command in executed_commands:
            command.await_cmd()
            command.save_data_to_db()

    def end(self):
        self.active = False


class PeriodicRegime(BaseTask):
    """
    Periodically call specified commands to change a regime.

    Fully customisable by two parameters:
    1. intervals - specifies periods when next set of commands should be called
        e.g. 'intervals': [8, 16],  # change regime after 8 hours and then after 16 hours
    2. commands  - list of commands for each regime change which should be executed
        e.g. 'commands': [[{'id': '10', 'args': [0, 20]}, {'id': '10', 'args': [1, 20]}],   # night
                         [{'id': '10', 'args': [0, 200]}, {'id': '10', 'args': [1, 200]}]]  # day

    Additional extra parameters:
    'device_id': str - ID of target device
    """
    def __init__(self, config):
        self.intervals = []
        self.commands = []
        self.device_id: str = ""

        self.__dict__.update(config)
        super(PeriodicRegime, self).__init__(config)

        self.device = app_manager.deviceManager.get_device(self.device_id)
        self.waiting = Event()

    def start(self):
        t = Thread(target=self._run)
        t.start()

    def _run(self):
        phase = 0
        while not self.waiting.is_set():
            self.execute_commands(self.commands[phase])
            self.waiting.wait(self.intervals[phase]*3600)  # to get seconds
            phase = (phase + 1) % len(self.intervals)

    def execute_commands(self, commands):
        executed_commands = []
        for item in commands:
            command = Command(self.device_id,
                              item.get("id"),
                              item.get("args", []),
                              self.task_id,
                              is_awaited=True)
            executed_commands.append(command)
            self.device.post_command(command, 1)

        for command in executed_commands:
            command.await_cmd()
            command.save_data_to_db()

    def end(self):
        self.waiting.set()
