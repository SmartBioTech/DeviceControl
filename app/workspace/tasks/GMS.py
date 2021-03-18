from threading import Thread
from time import sleep
from .. import Command, BaseTask
from ... import app_manager


class GMSMeasureAll(BaseTask):
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
        super(GMSMeasureAll, self).__init__(config)

    def start(self):
        t = Thread(target=self._run)
        t.start()
        
    def _run(self):
        cmd = Command(self.device_id, "1", [], self.task_id)
        self.device.post_command(cmd)
        while self.is_active:
            cmd = Command(self.device_id, "9", [], self.task_id)
            self.device.post_command(cmd)
            sleep(int(self.sleep_period))

    def end(self):
        self.is_active = False
