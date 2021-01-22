from threading import Thread
from time import sleep

import requests

from core.data.command import Command
from core.device.manager import DeviceManager
from core.task.abstract import BaseTask


class GMSMeasureAll(BaseTask):
    def __init__(self, config):
        self.__dict__.update(config)

        required = ['sleep_period', 'device_id', 'task_id']
        self.validate_attributes(required, type(self).__name__)

        self.device = DeviceManager().get_device(self.device_id)
        super(GMSMeasureAll, self).__init__()

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
