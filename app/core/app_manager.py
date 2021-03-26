from app.src.utils.response import Response
from app.src.utils import Log
from app.src.utils.errors import IdError
from app.src.utils.time import time_from_string


def validate_attributes(required, attributes, class_name):
    for att in required:
        if att not in attributes:
            raise AttributeError('{} must contain attribute {}'.format(class_name, att))
        else:
            if attributes[att] is None:
                raise AttributeError('The attribute {} of class {} cannot be None'.format(att, class_name))


class AppManager:
    def init_app(self):
        from app.src.task_manager import TaskManager
        from app.src.data_manager import DataManager
        from app.src.device_manager import DeviceManager

        self.taskManager = TaskManager()
        self.deviceManager = DeviceManager()
        self.dataManager = DataManager()

    def register_device(self, config: dict) -> Response:
        try:
            validate_attributes(['device_id', 'device_class', 'device_type', 'address'], config, 'Connector')
            device = self.deviceManager.new_device(config)
            self.dataManager.save_device(device)
        except (IdError, ModuleNotFoundError, AttributeError, KeyError) as e:
            Log.error(e)
            return Response(False, None, e)
        return Response(device is not None, None, None)

    def end_device(self, device_id: str) -> Response:
        try:
            self.deviceManager.remove_device(device_id)

            # TEMPORAL HACK !!!
            self.dataManager.update_experiment(device_id)

            return Response(True, None, None)
        except KeyError:
            exc = IdError('Connector with given ID: %s was not found' % device_id)
            Log.error(exc)
            return Response(False, None, exc)

    def command(self, config) -> Response:
        try:
            validate_attributes(['device_id', 'command_id'], config, 'Command')

            device_id = config.get('device_id')
            command_id = config.get('command_id')
            args = config.get('arguments', '[]')
            source = config.get('source', 'external')
            await_result = config.get('await', False)

            cmd = self.create_command(device_id, command_id, args, source)
            if await_result:
                self.deviceManager.get_device(device_id).post_command(cmd)
                cmd.await_cmd()
                return Response(True, cmd.response, None)
            else:
                self.deviceManager.get_device(device_id).post_manual_command(cmd)
                return Response(True, None, None)
        except AttributeError as e:
            Log.error(e)
            return Response(False, None, e)

    def register_task(self, config) -> Response:
        try:
            validate_attributes(['task_id', 'task_class', 'task_type'], config, 'Task')
            task = self.taskManager.create_task(config)
            task.start()
            return Response(True, None, None)
        except (IdError, TypeError, AttributeError) as e:
            Log.error(e)
            return Response(False, None, e)

    def end_task(self, task_id) -> Response:
        try:
            self.taskManager.remove_task(task_id)
            return Response(True, None, None)
        except KeyError:
            exc = IdError('Task with requested ID: %s was not found' % task_id)
            Log.error(exc)
            return Response(False, None, exc)

    def ping(self) -> Response:
        return Response(True, {
            'devices': self.deviceManager.ping(),
            'tasks': self.taskManager.ping()
        }, None)

    def get_data(self, config) -> Response:
        try:
            validate_attributes(['device_id', 'type'], config, 'GetData')
            
            device_id = config.get('device_id')
            data_type = config.get('type')  # (events/values)
            log_id = config.get('log_id', None)
            time = config.get('time', None)

            time = time_from_string(time)

            return Response(True, self.dataManager.get_data(log_id, time, device_id, data_type), None)
            
        except (IdError, AttributeError, SyntaxError) as e:
            Log.error(e)
            return Response(False, None, e)

    def get_latest_data(self, config) -> Response:
        try:
            validate_attributes(['device_id', 'type'], config, 'GetData')
            device_id = config.get('device_id')
            data_type = config.get('type')  # (events/values)
            return Response(True, self.dataManager.get_latest_data(device_id, data_type), None)

        except (IdError, AttributeError) as e:
            Log.error(e)
            return Response(False, None, e)

    @staticmethod
    def create_command(device_id, command_id, args, source):
        from ..command import Command
        return Command(device_id, command_id, eval(args), source)

    def end(self) -> Response:
        self.deviceManager.end()
        self.taskManager.end()
        return Response(True, None, None)
