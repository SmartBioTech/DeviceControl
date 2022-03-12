from collections import deque
from threading import Thread, Event
from time import sleep
from typing import Dict

from .. import Command, BaseTask, Observable, Observer
from ... import app_manager
from ...src.utils.mathlib import mean, median


class PBRMeasureAll(BaseTask):
    """
    Measures all measurable values and saves them to database.

    Automatically detects outliers for optical density.

    Extra parameters:

    - 'device_id': str - ID of target device,
    - 'sleep_period': float - measurement period,
    - 'max_outliers': int - maximum number of outliers on row,
    - 'pump_id': int - control pump ID,
    - 'lower_tol': int - lower outlier tolerance,
    - 'upper_tol': int - upper outlier tolerance,
    - 'od_attribute': int - OD channel to be used
    """
    def __init__(self, config):
        self.__dict__.update(config)

        required = ['sleep_period', 'lower_tol', 'upper_tol', 'od_attribute',
                    'max_outliers', 'device_id', 'pump_id']

        self.validate_attributes(required, type(self).__name__)

        self.latest_values = deque(maxlen=2)
        self.outliers = 0

        self.device = app_manager.deviceManager.get_device(self.device_id)
        self.average_od = self.measure_initial_od_average()
        self.od = Observable()

        super(PBRMeasureAll, self).__init__(config)

        self.commands_to_execute: Dict[str, dict] = {
            "pwm_settings": {
                "id": "12"
            },
            "light_0": {
                "id": "9",
                "args": [0]
            },
            "light_1": {
                "id": "9",
                "args": [1]
            },
            "od_0": {
                "id": "5",
                "args": [0, 30]
            },
            "od_1": {
                "id": "5",
                "args": [1, 30]
            },
            "ph": {
                "id": "4",
                "args": [5, 0]
            },
            "temp": {
                "id": "2"
            },
            "pump": {
                "id": "6",
                "args": [self.pump_id]
            },
            "o2": {
                "id": "14"
            },
            "ft_0": {
                "id": "17",
                "args": [0]
            },
            "ft_1": {
                "id": "17",
                "args": [1]
            }
        }

    def get_od_for_init(self):
        """
        Measure sample value of OD.

        :return: obtained value
        """
        cmd = Command(self.device_id, "5",
                      [self.od_attribute],
                      self.task_id,
                      is_awaited=True)

        self.device.post_command(cmd)
        cmd.await_cmd()
        if cmd.is_valid:
            return cmd.response

    def measure_initial_od_average(self):
        """
        Collect the OD value from 5 measurements and
        calculate the average OD from the measured data.

        :return: measured value
        """
        data = []
        while len(data) < 5:
            od = self.get_od_for_init()
            if od is not None:
                data.append(od['od'])

        data.sort()
        computed = False
        average = 0

        while not computed:
            mean_value = mean(data)
            median_value = median(data)

            if len(data) < 2:
                computed = True
                average = data[0]

            if mean_value / median_value <= 1:

                if mean_value / median_value >= 0.9:
                    computed = True
                    average = mean_value
                else:
                    data = data[1:]
            else:
                data = data[:-1]
        return average

    def handle_outlier(self, measured_od) -> bool:
        """
        Decides whether the measured OD value is an outlier or not.

        :param measured_od: optical density value
        :return: True if it is an outlier, False otherwise
        """
        lower_tol = self._calculate_tolerance(-self.lower_tol)
        upper_tol = self._calculate_tolerance(self.upper_tol)

        if lower_tol <= measured_od <= upper_tol:
            self.outliers = 0
            self.average_od = self.calculate_average()
            return False
        else:
            self.outliers += 1
            if self.outliers > self.max_outliers:
                self.outliers = 0
                self.average_od = self.calculate_average()
                return False
            else:
                return True

    def _calculate_tolerance(self, value):
        return ((100 + value) / 100) * self.average_od

    def calculate_average(self):
        """
        Helper method which calculates the average of a list while removing the elements from the objects deque.

        :return: The average of the deque
        """
        my_list = []
        while self.latest_values:
            my_list.append(self.latest_values.pop())

        return sum(my_list) / len(my_list)

    def start(self):
        """
        Start the task.
        """
        t = Thread(target=self._run)
        t.start()

    def _run(self):
        self.average_od = self.measure_initial_od_average()
        od_variant = 'od_1' if self.od_attribute == 1 else 'od_0'

        while self.is_active:
            commands = []

            for _name, _command in self.commands_to_execute.items():
                command = Command(self.device_id,
                                  _command.get("id"),
                                  _command.get("args", []),
                                  self.task_id,
                                  is_awaited=True)
                commands.append((_name, command))
                self.device.post_command(command, 1)

            for name, command in commands:
                command.await_cmd()
                if command.is_valid and name == od_variant:
                    od = command.response['od']
                    self.latest_values.appendleft(od)
                    od_is_outlier = self.handle_outlier(od)
                    if not od_is_outlier:
                        self.od.value = od
                    command.response = {'od': od, 'outlier': od_is_outlier, 'attribute': self.od_attribute}
                command.save_data_to_db()

            sleep(self.sleep_period)

    def end(self):
        """
        End the task.
        """
        self.is_active = False


class ePBRMeasureAll(PBRMeasureAll):
    """
    Measures all measurable values and saves them to database.

    Extra parameters:
    'device_id': str - ID of target device,
    'sleep_period': float - measurement period
    """
    def __init__(self, config):
        super(ePBRMeasureAll, self).__init__(config)
        self.commands_to_execute: Dict[str, dict] = {
            "od_0": {
                "id": "5",
                "args": [0]
            },
            "od_1": {
                "id": "5",
                "args": [1]
            },
            "ph": {
                "id": "4"
            },
            "temp": {
                "id": "2"
            }
        }


class PBRGeneralPump(BaseTask, Observer):
    """
    Turbidostat task based on optical density (OD) values.

    Turns on/off (by specifying command for that) when OD reaches max_od/min_od value.

    Extra parameters:

    - 'min_od': int - lowed OD bound,
    - 'max_od': int - upper OD bound,
    - 'device_id': str - ID of target device,
    - 'measure_all_task_id': str - associated measurement task,
    - 'pump_on_command': dict- command to turn on pump,
    - 'pump_off_command': dict - command to turn off pump
    """
    def __init__(self, config):
        self.__dict__.update(config)

        required = ['min_od', 'max_od', 'device_id', 'measure_all_task_id',
                    'pump_on_command', 'pump_off_command']

        self.validate_attributes(required, type(self).__name__)

        self.is_pump_on = False

        self.device = app_manager.deviceManager.get_device(self.device_id)
        self.od_task = app_manager.taskManager.get_task(self.measure_all_task_id)

        self.od_task.od.observe(self)

        super(PBRGeneralPump, self).__init__(config)

    def get_pump_command(self, state: bool) -> Command:
        """
        Create command to change pump state.

        :param state: desired pump state
        :return: create Command
        """
        if state:
            return Command(self.device_id, self.pump_on_command.get("command_id"),
                           eval(self.pump_on_command.get("arguments", "[]")), self.task_id)
        else:
            return Command(self.device_id, self.pump_off_command.get("command_id"),
                           eval(self.pump_off_command.get("arguments", "[]")), self.task_id)

    def update(self, observable: Observable):
        self.stabilize(observable.value)

    def start(self):
        """
        Start the task.
        """
        pass

    def end(self):
        """
        End the task.
        """
        pass

    def is_od_value_too_high(self, od):
        return od > self.max_od

    def is_od_value_too_low(self, od):
        return od < self.min_od

    def turn_pump_on(self):
        self.change_pump_state(True)

    def turn_pump_off(self):
        self.change_pump_state(False)

    def change_pump_state(self, state: bool):
        """
        Switch state of the pump.

        :param state: target state
        """
        for try_n in range(5):
            command = self.get_pump_command(state)
            self.device.post_command(command, 1)
            command.await_cmd()

            if isinstance(command.response['success'], bool) and command.response['success']:
                command.save_command_to_db()
                self.is_pump_on = state
                return
        raise ConnectionError

    def stabilize(self, od):
        """
        Update state of pump if OD is out of allowed bounds

        :param od: current OD
        """
        if self.is_od_value_too_high(od):
            if not self.is_pump_on:
                self.turn_pump_on()
        elif self.is_od_value_too_low(od):
            if self.is_pump_on:
                self.turn_pump_off()
