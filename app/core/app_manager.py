from app.src.utils.logger import log_initialise, log_terminate, log_terminate_all
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
    """
    Defines entry points to the application.
    """

    def init_app(self):
        """
        Initializes the application.
        """
        from app.src.task_manager import TaskManager
        from app.src.data_manager import DataManager
        from app.src.device_manager import DeviceManager

        self.taskManager = TaskManager()
        self.deviceManager = DeviceManager()
        self.dataManager = DataManager()

    @log_initialise('device')
    def register_device(self, config: dict) -> Response:
        """
        Register a new device.
        For reference, see https://github.com/SmartBioTech/DeviceControl/wiki/End-Points#device-initiation

        :param config: A dictionary with pre-defined keys
        :return: Response object
        """
        try:
            validate_attributes(['device_id', 'device_class', 'device_type', 'address'], config, 'Connector')
            device = self.deviceManager.new_device(config)
            self.dataManager.save_device(device)
            self.dataManager.event_device_start(config)
        except (IdError, ModuleNotFoundError, AttributeError, KeyError) as e:
            Log.error(e)
            return Response(False, None, e)
        return Response(device is not None, None, None)

    @log_terminate
    def end_device(self, device_id: str) -> Response:
        """
        Terminates an existing device.

        :param device_id: ID of an existing device
        :return: Response object
        """
        try:
            self.deviceManager.remove_device(device_id)
            self.dataManager.event_device_end(device_id)

            # TEMPORAL HACK !!!
            self.dataManager.update_experiment(device_id)

            return Response(True, None, None)
        except KeyError:
            exc = IdError('Connector with given ID: %s was not found' % device_id)
            Log.error(exc)
            return Response(False, None, exc)

    def command(self, config: dict) -> Response:
        """
        Run a specific command.
        For reference, see https://github.com/SmartBioTech/DeviceControl/wiki/End-Points#command

        :param config: A dictionary with pre-defined keys
        :return: Response object
        """
        try:
            validate_attributes(['device_id', 'command_id'], config, 'Command')

            device_id = config.get('device_id')
            command_id = config.get('command_id')
            args = config.get('arguments', '[]')
            source = config.get('source', 'external')
            await_result = config.get('await', False)

            cmd = self._create_command(device_id, command_id, args, source)
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

    @log_initialise('task')
    def register_task(self, config: dict) -> Response:
        """
        Register a new task.
        For reference, see https://github.com/SmartBioTech/DeviceControl/wiki/End-Points#task-initiation

        :param config: A dictionary with pre-defined keys
        :return: Response object
        """
        try:
            validate_attributes(['task_id', 'task_class', 'task_type'], config, 'Task')
            task = self.taskManager.create_task(config)
            task.start()
            self.dataManager.event_task_start(config)
            return Response(True, None, None)
        except (IdError, TypeError, AttributeError) as e:
            Log.error(e)
            return Response(False, None, e)

    @log_terminate
    def end_task(self, task_id) -> Response:
        """
        Terminate an existing task.

        :param task_id: ID of an existing task
        :return: Response object
        """
        try:
            device_id = self.taskManager.remove_task(task_id)
            self.dataManager.event_task_end(device_id, task_id)
            return Response(True, None, None)
        except KeyError:
            exc = IdError('Task with requested ID: %s was not found' % task_id)
            Log.error(exc)
            return Response(False, None, exc)

    def ping(self) -> Response:
        """
        Test the application responsiveness.

        :return: Response object
        """
        return Response(True, {
            'devices': self.deviceManager.ping(),
            'tasks': self.taskManager.ping()
        }, None)

    def get_data(self, config: dict) -> Response:
        """
        Retrieves data in supported format as specified at https://github.com/SmartBioTech/DeviceControl/wiki/End-Points#get-data

        :param config: A dictionary with pre-defined keys
        :return: Response object
        """
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
        """
        Retrieves the last data entry for specified Device ID and Data Type.

        :param config: A dictionary which specifies the "device_id": string and "type": string
        :return: Response object
        """
        try:
            validate_attributes(['device_id', 'type'], config, 'GetData')
            device_id = config.get('device_id')
            data_type = config.get('type')  # (events/values)
            return Response(True, self.dataManager.get_latest_data(device_id, data_type), None)

        except (IdError, AttributeError) as e:
            Log.error(e)
            return Response(False, None, e)

    @log_terminate_all
    def end(self) -> Response:
        """
        Ends the application. For reference, see https://github.com/SmartBioTech/DeviceControl/wiki/End-Points#end

        :return: Response object
        """
        self.taskManager.end()
        self.deviceManager.end()
        return Response(True, None, None)

    @staticmethod
    def _create_command(device_id, command_id, args, source):
        from ..command import Command
        return Command(device_id, command_id, eval(args), source)

    def _restore_session(self):
        # first start devices
        tasks = []
        for log in self.dataManager.load_log():
            from app.models import LogType
            if log.type == LogType.DEVICE:
                self.register_device(log.config)
            else:
                tasks.append(log)

        # finally start tasks
        for task in tasks:
            self.register_task(task.config)
