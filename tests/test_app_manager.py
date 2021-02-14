import unittest
from unittest import mock

from app.command import Command
from app.src.utils.errors import IdError
from app import create_app, db, app_manager
from app.src.utils.response import Response


class AppManagerTestCases(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_device(self):
        config = {'device_id': 15, 'device_class': 'name', 'device_type': 'car', 'address': 'home'}
        device = mock.Mock()
        app_manager.deviceManager.new_device = mock.Mock(return_value=device)
        app_manager.dataManager.save_device = mock.Mock()

        # correct behaviour
        result = Response(True, None, None)
        self.assertEqual(app_manager.register_device(config), result)

        # exception in progress
        e = AttributeError("Device missing attribute")
        result = Response(False, None, e)
        app_manager.deviceManager.new_device = mock.Mock(side_effect=e)

        self.assertEqual(app_manager.register_device(config), result)

    def test_end_device(self):
        device_id = 23
        app_manager.deviceManager.remove_device = mock.Mock()
        app_manager.dataManager.update_experiment = mock.Mock()

        # correct behaviour
        result = Response(True, None, None)
        self.assertEqual(app_manager.end_device(device_id), result)

        # exception in progress
        e = IdError('Connector with given ID: %s was not found' % device_id)
        app_manager.deviceManager.remove_device = mock.Mock(side_effect=KeyError)
        result = Response(False, None, e)
        self.assertEqual(app_manager.end_device(device_id), result)

    def test_command(self):
        config = {'device_id': 23, 'command_id': '3', 'arguments': '[30]'}
        result = Command(23, '3', [30], 'external')
        result.save_command_to_db = mock.Mock()

        device = mock.Mock()
        device.post_command = mock.Mock()
        app_manager.deviceManager.get_device = mock.Mock(return_value=device)

        # correct behaviour
        result = Response(True, None, None)
        app_manager.dataManager.save_event = mock.Mock()
        self.assertEqual(app_manager.command(config), result)

        # exception in progress
        e = AttributeError("Command missing attribute")
        result = Response(False, None, e)
        app_manager.deviceManager.get_device = mock.Mock(side_effect=e)
        self.assertEqual(app_manager.command(config), result)

    def test_register_task(self):
        config = {'task_id': 23, 'task_class': 'PSI', 'task_type': 'PBR_measure_all'}
        task = mock.Mock()
        task.start = mock.Mock()
        app_manager.taskManager.create_task = mock.Mock(return_value=task)

        # correct behaviour
        result = Response(True, None, None)
        self.assertEqual(app_manager.register_task(config), result)

        # exception in progress
        e = AttributeError("Task missing attribute")
        result = Response(False, None, e)
        app_manager.taskManager.create_task = mock.Mock(side_effect=e)
        self.assertEqual(app_manager.register_task(config), result)

    def test_end_task(self):
        task_id = 23
        app_manager.taskManager.remove_task = mock.Mock()

        # correct behaviour
        result = Response(True, None, None)
        self.assertEqual(app_manager.end_task(task_id), result)

        # exception in progress
        e = IdError("Task with requested ID: 23 was not found")
        result = Response(False, None, e)
        app_manager.taskManager.remove_task = mock.Mock(side_effect=KeyError)
        self.assertEqual(app_manager.end_task(task_id), result)

    def test_ping(self):
        device_data = {'device_data': 'data01'}
        task_data = {'task_data': 'data02'}
        app_manager.deviceManager.ping = mock.Mock(return_value=device_data)
        app_manager.taskManager.ping = mock.Mock(return_value=task_data)

        # correct behaviour
        result = Response(True, {'devices': device_data, 'tasks': task_data}, None)
        self.assertEqual(app_manager.ping(), result)

    def get_data(self):
        config = {'time': '20211010101010333', 'device_id': 23, 'type': 'values'}
        data = {'some random data': 123}
        app_manager.dataManager.get_data = mock.Mock(return_value=data)

        # correct behaviour
        result = Response(True, data, None)
        self.assertEqual(app_manager.get_data(config), result)

        # exception in progress
        e = AttributeError("Missing a key attribute.")
        result = Response(False, None, e)
        app_manager.dataManager.get_data = mock.Mock(side_effect=e)
        self.assertEqual(app_manager.get_data(config), result)

    def test_get_latest_data(self):
        config = {'device_id': 23, 'type': 'values'}
        data = {'some random data': 123}
        app_manager.dataManager.get_latest_data = mock.Mock(return_value=data)

        # correct behaviour
        result = Response(True, data, None)
        self.assertEqual(app_manager.get_latest_data(config), result)

        # exception in progress
        e = AttributeError("Missing a key attribute.")
        result = Response(False, None, e)
        app_manager.dataManager.get_latest_data = mock.Mock(side_effect=e)
        self.assertEqual(app_manager.get_latest_data(config), result)
