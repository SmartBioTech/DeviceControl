from core.data.manager import DataManager
from core.data.command import Command
from core.log import Log
from  core.device.manager import DeviceManager
from core.task.manager import TaskManager
from core.utils.errors import IdError


class AppManager:
    def __init__(self, taskManager: TaskManager, deviceManager: DeviceManager, dataManager: DataManager):
        self.taskManager = taskManager
        self.deviceManager = deviceManager
        self.dataManager = dataManager

    def register_device(self, config: dict) -> (bool, str):
        try:
            device = self.deviceManager.new_device(config)
        except (IdError, ModuleNotFoundError, AttributeError) as e:
            Log.error(e)
            return False

        return device is not None

    def end_device(self, device_id: str):
        try:
            self.deviceManager.remove_device(device_id)
            return True
        except AttributeError:
            Log.error(IdError("Connector with given ID: %s was not found" % device_id))
            return False

    def command(self, device_id, command_id, args, source, priority=False):
        try:
            cmd = Command(device_id, command_id, eval(args), source)
            if priority:
                self.deviceManager.get_device(device_id).post_command(cmd, priority=1)
            else:
                self.deviceManager.get_device(device_id).post_command(cmd)
            return True
        except (IdError, AttributeError) as e:
            Log.error(e)
            return False

    def register_task(self, config):
        try:
            task = self.taskManager.create_task(config)
            task.start()
            return True
        except (IdError, TypeError) as e:
            Log.error(e)
            return False

    def end_task(self, task_id):
        try:
            self.taskManager.remove_task(task_id)
            return True
        except IdError as e:
            Log.error(e)
            return False

    def ping(self) -> dict:
        return {
            "devices": self.deviceManager.ping(),
            "tasks": self.taskManager.ping()
        }

    def get_data(self, device_id, log_id):
        return self.dataManager.get_data_by_id(log_id, device_id)

    def end(self):
        self.deviceManager.end()
        self.taskManager.end()
