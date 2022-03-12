import unittest
from unittest import mock

from app import create_app, db, app_manager
from app.src.task_manager import TaskManager
from app.src.utils.errors import IdError
from app.workspace.tasks import PBR


class TaskManagerTestCases(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.TM = TaskManager()
        self.config = {'task_id': 23, 'task_class': 'PSI', 'task_type': 'PBR_measure_all', 'sleep_period': 5,
                       'lower_tol': 0.1, 'upper_tol': 0.5, 'od_attribute': 5, 'max_outliers': 6,
                       'device_id': '2', 'pump_id': 5}

        dev_config = {"device_class": 'test', "device_type": 'PBR', "device_id": '2', 'address': "home"}
        app_manager.dataManager._store_permanent()
        app_manager.register_device(dev_config)

    def tearDown(self):
        app_manager.end_device('2')
        self.TM.end()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_load_class(self):
        # correct case
        task_class = 'PSI'
        task_type = 'PBR_measure_all'

        expected_class = PBR.PBRMeasureAll
        result = self.TM._load_class(task_class, task_type)
        self.assertEqual(expected_class, result)

        # unknown class
        device_class = 'Magic'
        device_type = 'PBR'
        self.assertRaises(KeyError, self.TM._load_class, device_class, device_type)

        # unknown type
        device_class = 'PSI'
        device_type = 'Magic'
        self.assertRaises(KeyError, self.TM._load_class, device_class, device_type)

    def test_create_task(self):
        correct_task = PBR.PBRMeasureAll(self.config)
        self.TM._load_class = mock.Mock(return_value=PBR.PBRMeasureAll)
        task = self.TM.create_task(self.config)
        self.assertEqual(correct_task, task)

        self.assertRaises(IdError, self.TM.create_task, self.config)
        correct_task.end()

        config = dict(self.config)
        config.pop('upper_tol')
        self.assertRaises(IdError, self.TM.create_task, config)

    def test_remove_task(self):
        task = PBR.PBRMeasureAll(self.config)
        self.TM.tasks[self.config["task_id"]] = task
        self.TM.remove_task(self.config["task_id"])
        self.assertEqual(self.TM.tasks, dict())

    def test_get_task(self):
        task = PBR.PBRMeasureAll(self.config)
        self.TM.tasks[self.config["task_id"]] = task
        self.assertEqual(self.TM.get_task(self.config["task_id"]), task)

        self.assertRaises(IdError, self.TM.get_task, 2)

    def test_end(self):
        task = PBR.PBRMeasureAll(self.config)
        self.TM.tasks[self.config["task_id"]] = task

        self.TM.end()
        self.assertEqual(self.TM.tasks, dict())

    def test_ping(self):
        task = PBR.PBRMeasureAll(self.config)
        self.TM.tasks[self.config["task_id"]] = task

        result = {self.config["task_id"]: True}

        self.assertEqual(self.TM.ping(), result)
