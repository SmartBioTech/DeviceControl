from core.data.log import Logger
from core.device_module.command import Command
from core.device_module.device_manager import DeviceManager
from core.task_module.task_manager import TaskManager
from core.utils.errors import IdError


class AppManager:
    def __init__(self):
        self.taskManager = TaskManager()
        self.deviceManager = DeviceManager()

    def register_device(self, config: dict) -> (bool, str):
        try:
            device = self.deviceManager.new_device(config)
        except (IdError, ModuleNotFoundError) as e:
            Logger().error(e)
            return False

        return device is not None

    def end_device(self, device_id: str):
        try:
            self.deviceManager.remove_device(device_id)
            return True
        except AttributeError:
            Logger().error(IdError("Device with given ID: %s was not found" % device_id))
            return False

    def command(self, device_id, command_id, args, source):
        try:
            cmd = Command(device_id, int(command_id), eval(args), source)
            self.deviceManager.get_device(device_id).post_command(cmd)
            return True
        except (IdError, AttributeError) as e:
            Logger().error(e)
            return False

    def register_task(self, config):
        try:
            task = self.taskManager.create_task(config)
            task.start()
            return True
        except (IdError, TypeError) as e:
            Logger().error(e)
            return False

    def end_task(self, task_id):
        try:
            self.taskManager.remove_task(task_id)
            return True
        except IdError as e:
            Logger().error(e)
            return False

    def ping(self) -> dict:
        return {
            "devices": self.deviceManager.ping(),
            "tasks": self.taskManager.ping()
        }

    def end(self):
        self.deviceManager.end()
        self.taskManager.end()
