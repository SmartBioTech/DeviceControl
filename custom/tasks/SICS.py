from threading import Thread
from time import sleep

import requests

from core.data.command import Command
from core.device.manager import DeviceManager
from core.task.abstract import BaseTask


class MeasureWeight(BaseTask):
    def __init__(self, config):
        self.sleep_period = None
        self.device_id: str = ""
        self.task_id = None

        self.__dict__.update(config)

        try:
            assert self.sleep_period is not None
            assert self.device_id is not None
            assert self.task_id != ""
            
        except AssertionError:
            raise AttributeError("Configuration of MeasureWeight task must contain all required attributes")

        self.device = DeviceManager().get_device(self.device_id)
        super(MeasureWeight, self).__init__()

    def start(self):
        t = Thread(target=self._run)
        t.start()

    def _run(self):
        while self.is_active:
            cmd = Command(self.device_id, "1", [], self.task_id)
            self.device.post_command(cmd)
            sleep(int(self.sleep_period))

    def end(self):
        self.is_active = False
