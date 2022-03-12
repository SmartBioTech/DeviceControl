from threading import Thread
from time import sleep

from .. import Command, BaseTask
from ... import app_manager


class MeasureAll(BaseTask):
    """
    Measures all measurable values and saves them to database.

    Extra parameters:

    - 'device_id': str - ID of target device,
    - 'sleep_period': float - measurement period
    """
    def __init__(self, config):
        self.__dict__.update(config)

        required = ['sleep_period', 'device_id', 'task_id']
        self.validate_attributes(required, type(self).__name__)

        self.device = app_manager.deviceManager.get_device(self.device_id)
        super(MeasureAll, self).__init__(config)

    def start(self):
        """
        Start the task.
        """
        t = Thread(target=self._run)
        t.start()

    def _run(self):
        while self.is_active:
            cmd = Command(self.device_id, "3", [], self.task_id)
            self.device.post_command(cmd)
            sleep(int(self.sleep_period))

    def end(self):
        """
        End the task.
        """
        self.is_active = False
