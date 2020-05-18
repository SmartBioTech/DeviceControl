from typing import Tuple, Optional

from core.data.command import Command
from core.data.manager import DataManager
from core.device.manager import DeviceManager
from core.log import Log
from core.task.manager import TaskManager
from core.utils.errors import IdError
from core.utils.singleton import singleton
from core.utils.time import process_time


@singleton
class AppManager:
    def __init__(self,
                 taskManager: TaskManager = None,
                 deviceManager: DeviceManager = None,
                 dataManager: DataManager = None
                 ):
        self.taskManager: TaskManager = taskManager
        self.deviceManager: DeviceManager = deviceManager
        self.dataManager: DataManager = dataManager

    def register_device(self, config: dict) -> (bool, Optional[Exception], None):
        try:
            device = self.deviceManager.new_device(config)
        except (IdError, ModuleNotFoundError, AttributeError) as e:
            Log.error(e)
            return False, e, None

        return device is not None, None, None

    def end_device(self, config: dict):
        device_id = config.get("target_id")
        try:
            self.deviceManager.remove_device(device_id)
            return True, None, None
        except AttributeError:
            exc = IdError("Connector with given ID: %s was not found" % device_id)
            Log.error(exc)
            return False, exc, None

    def command(self, config: dict):
        device_id = config.get("device_id")
        command_id = config.get("command_id")
        args = config.get("arguments", "[]")
        source = config.get("source", "external")
        try:
            cmd = Command(device_id, command_id, eval(args), source)
            self.deviceManager.get_device(device_id).post_command(cmd)
            return True, None, None
        except (IdError, AttributeError) as e:
            Log.error(e)
            return False, e, None

    def register_task(self, config: dict):
        try:
            task = self.taskManager.create_task(config)
            task.start()
            return True, None, None
        except (IdError, TypeError) as e:
            Log.error(e)
            return False, e, None

    def end_task(self, config: dict):
        task_id = config.get("target_id")
        try:
            self.taskManager.remove_task(task_id)
            return True, None, None
        except IdError as e:
            Log.error(e)
            return False, e, None

    def ping(self) -> Tuple[bool, Optional[Exception], dict]:
        return True, None, {
            "devices": self.deviceManager.ping(),
            "tasks": self.taskManager.ping()
        }

    def get_data(self, config: dict):
        device_id = config.get("device_id", None)
        log_id = config.get("log_id", None)
        time = config.get("time", None)
        if time is not None:
            try:
                time = process_time(time)
            except SyntaxError as e:
                return False, e, None
        return True, None, self.dataManager.get_data(log_id, time, device_id)

    def end(self):
        self.deviceManager.end()
        self.taskManager.end()
        return True, None, None
