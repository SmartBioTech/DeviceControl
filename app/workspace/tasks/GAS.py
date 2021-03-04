from threading import Thread
from time import sleep
from .. import Command, BaseTask
from ... import app_manager


class GASMeasureAll(BaseTask):
    def __init__(self, config):
        self.__dict__.update(config)

        required = ['sleep_period', 'device_id', 'task_id']
        self.validate_attributes(required, type(self).__name__)

        self.device = app_manager.deviceManager.get_device(self.device_id)
        super(GASMeasureAll, self).__init__(config)

    def start(self):
        t = Thread(target=self._run)
        t.start()

    def _run(self):
        while self.is_active:
            command_msg = {
                "device_id": self.device_id,
                "command_id": "6",
                "source": self.task_id
            }

            cmd = Command(self.device_id, "6", [], self.task_id)
            self.device.post_command(cmd)
            sleep(int(self.sleep_period))

    def end(self):
        self.is_active = False
