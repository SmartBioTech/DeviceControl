from core.data.command import Command
from core.data.manager import DataManager
from core.data.model import Response
from core.device.manager import DeviceManager
from core.log import Log
from core.task.manager import TaskManager
from core.utils.errors import IdError
from core.utils.singleton import singleton


@singleton
class AppManager:
    def __init__(self, taskManager: TaskManager, deviceManager: DeviceManager, dataManager: DataManager):
        self.taskManager: TaskManager = taskManager
        self.deviceManager: DeviceManager = deviceManager
        self.dataManager: DataManager = dataManager

    def register_device(self, config: dict) -> Response:
        try:
            device = self.deviceManager.new_device(config)
            self.dataManager.save_device(device)
        except (IdError, ModuleNotFoundError, AttributeError) as e:
            Log.error(e)
            return Response(False, None, e)

        return Response(device is not None, None)

    def end_device(self, device_id: str) -> Response:
        try:
            self.deviceManager.remove_device(device_id)

            # TEMPORAL HACK !!!
            self.dataManager.update_experiment(device_id)

            return Response(True, None)
        except AttributeError:
            exc = IdError("Connector with given ID: %s was not found" % device_id)
            Log.error(exc)
            return Response(False, None, exc)

    def command(self, device_id, command_id, args, source, priority=False) -> Response:
        try:
            cmd = Command(device_id, command_id, eval(args), source)
            if priority:
                self.deviceManager.get_device(device_id).post_command(cmd, priority=1)
            else:
                self.deviceManager.get_device(device_id).post_command(cmd)
            return Response(True, None)
        except (IdError, AttributeError) as e:
            Log.error(e)
            return Response(False, None, e)

    def register_task(self, config) -> Response:
        try:
            task = self.taskManager.create_task(config)
            task.start()
            return Response(True, None)
        except (IdError, TypeError) as e:
            Log.error(e)
            return Response(False, None, e)

    def end_task(self, task_id) -> Response:
        try:
            self.taskManager.remove_task(task_id)
            return Response(True, None)
        except IdError as e:
            Log.error(e)
            return Response(False, None, e)

    def ping(self) -> Response:
        return Response(True, {
            "devices": self.deviceManager.ping(),
            "tasks": self.taskManager.ping()
        })

    def get_data(self, device_id, log_id=None, time=None, data_type='values') -> Response:
        return Response(True, self.dataManager.get_data(log_id, time, device_id, data_type))

    def get_latest_data(self, device_id=None, data_type='values') -> Response:
        return Response(True, self.dataManager.get_latest_data(device_id=device_id, data_type=data_type))

    def end(self) -> Response:
        self.deviceManager.end()
        self.taskManager.end()
        return Response(True, None)
