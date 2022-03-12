from threading import Thread
from time import sleep
from .. import Command, BaseTask
from ... import app_manager


class GASMeasureAll(BaseTask):
    """
    Measures all measurable values and saves them to database.

    Extra parameters:

    'device_id': str - ID of target device,
    'sleep_period': float - measurement period
    """
    def __init__(self, config):
        self.__dict__.update(config)

        required = ['sleep_period', 'device_id', 'task_id']
        self.validate_attributes(required, type(self).__name__)

        self.device = app_manager.deviceManager.get_device(self.device_id)
        super(GASMeasureAll, self).__init__(config)

        self.commands_to_execute = {
            "co2_air": {
                "id": "7"
            },
            "flow": {
                "id": "1"
            },
        }

    def start(self):
        """
        Start the task.
        """
        t = Thread(target=self._run)
        t.start()

    def _run(self):
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
                command.save_data_to_db()

            sleep(self.sleep_period)

    def end(self):
        """
        End the task.
        """
        self.is_active = False
