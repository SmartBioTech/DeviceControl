import unittest
from unittest import mock

from app.command import Command
from app.src.utils.errors import IdError
from app import create_app, db, AppManager
from app.src.utils.response import Response


class AppManagerTestCases(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        self.AM = AppManager()
        self.AM.init_app()
        self.AM.dataManager.store_permanent()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_device(self):
        config = {'device_id': 15, 'device_class': 'name', 'device_type': 'car', 'address': 'home'}
        device = mock.Mock()
        self.AM.deviceManager.new_device = mock.Mock(return_value=device)
        self.AM.dataManager.save_device = mock.Mock()
        self.AM.dataManager.event_device_start = mock.Mock()

        # correct behaviour
        result = Response(True, None, None)
        self.assertEqual(self.AM.register_device(config), result)

        # exception in progress
        e = AttributeError("Device missing attribute")
        result = Response(False, None, e)
        self.AM.deviceManager.new_device = mock.Mock(side_effect=e)

        self.assertEqual(self.AM.register_device(config), result)

    def test_end_device(self):
        device_id = 23
        self.AM.deviceManager.remove_device = mock.Mock()
        self.AM.dataManager.update_experiment = mock.Mock()
        self.AM.dataManager.event_device_end = mock.Mock()

        # correct behaviour
        result = Response(True, None, None)
        self.assertEqual(self.AM.end_device(device_id), result)

        # exception in progress
        e = IdError('Connector with given ID: %s was not found' % device_id)
        self.AM.deviceManager.remove_device = mock.Mock(side_effect=KeyError)
        result = Response(False, None, e)
        self.assertEqual(self.AM.end_device(device_id), result)

    def test_command(self):
        config = {'device_id': 23, 'command_id': '3', 'arguments': '[30]'}
        result = Command(23, '3', [30], 'external')
        result.save_command_to_db = mock.Mock()

        device = mock.Mock()
        device.post_command = mock.Mock()
        self.AM.deviceManager.get_device = mock.Mock(return_value=device)

        # correct behaviour
        result = Response(True, None, None)
        command = mock.Mock()
        command.save_command_to_db = mock.Mock()
        self.AM.create_command = mock.Mock(return_value=device)
        self.assertEqual(self.AM.command(config), result)

        # exception in progress
        e = AttributeError("Command missing attribute")
        result = Response(False, None, e)
        self.AM.deviceManager.get_device = mock.Mock(side_effect=e)
        self.assertEqual(self.AM.command(config), result)

    def test_register_task(self):
        config = {'task_id': 23, 'task_class': 'PSI', 'task_type': 'PBR_measure_all'}
        task = mock.Mock()
        task.start = mock.Mock()
        self.AM.taskManager.create_task = mock.Mock(return_value=task)
        self.AM.dataManager.event_task_start = mock.Mock()

        # correct behaviour
        result = Response(True, None, None)
        self.assertEqual(self.AM.register_task(config), result)

        # exception in progress
        e = AttributeError("Task missing attribute")
        result = Response(False, None, e)
        self.AM.taskManager.create_task = mock.Mock(side_effect=e)
        self.assertEqual(self.AM.register_task(config), result)

    def test_end_task(self):
        task_id = 23
        self.AM.taskManager.remove_task = mock.Mock()
        self.AM.dataManager.event_task_end = mock.Mock()

        # correct behaviour
        result = Response(True, None, None)
        self.assertEqual(self.AM.end_task(task_id), result)

        # exception in progress
        e = IdError("Task with requested ID: 23 was not found")
        result = Response(False, None, e)
        self.AM.taskManager.remove_task = mock.Mock(side_effect=KeyError)
        self.assertEqual(self.AM.end_task(task_id), result)

    def test_ping(self):
        device_data = {'device_data': 'data01'}
        task_data = {'task_data': 'data02'}
        self.AM.deviceManager.ping = mock.Mock(return_value=device_data)
        self.AM.taskManager.ping = mock.Mock(return_value=task_data)

        # correct behaviour
        result = Response(True, {'devices': device_data, 'tasks': task_data}, None)
        self.assertEqual(self.AM.ping(), result)

    def get_data(self):
        config = {'time': '20211010101010333', 'device_id': 23, 'type': 'values'}
        data = {'some random data': 123}
        self.AM.dataManager.get_data = mock.Mock(return_value=data)

        # correct behaviour
        result = Response(True, data, None)
        self.assertEqual(self.AM.get_data(config), result)

        # exception in progress
        e = AttributeError("Missing a key attribute.")
        result = Response(False, None, e)
        self.AM.dataManager.get_data = mock.Mock(side_effect=e)
        self.assertEqual(self.AM.get_data(config), result)

    def test_get_latest_data(self):
        config = {'device_id': 23, 'type': 'values'}
        data = {'some random data': 123}
        self.AM.dataManager.get_latest_data = mock.Mock(return_value=data)

        # correct behaviour
        result = Response(True, data, None)
        self.assertEqual(self.AM.get_latest_data(config), result)

        # exception in progress
        e = AttributeError("Missing a key attribute.")
        result = Response(False, None, e)
        self.AM.dataManager.get_latest_data = mock.Mock(side_effect=e)
        self.assertEqual(self.AM.get_latest_data(config), result)
