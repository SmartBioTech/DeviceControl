import unittest
from unittest import mock

from app.models import Device, Value, Variable, VariableType, Experiment
from app.src.device_manager import DeviceManager
from app import create_app, db
from app.src.utils.permanent_data import VARIABLES
from app.src.utils.time import now
from app.workspace.devices.PSI import java


class DataManagerTestCases(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.DM = DeviceManager()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_load_class(self):
        # correct case
        device_class = 'PSI'
        device_type = 'PBR'

        expected_class = java.PBR
        result = self.DM.load_class(device_class, device_type)
        self.assertEqual(expected_class, result)

        # unknown class
        device_class = 'Magic'
        device_type = 'PBR'
        self.assertRaises(AttributeError, self.DM.load_class, device_class, device_type)

        # unknown type
        device_class = 'PBR'
        device_type = 'Magic'
        self.assertRaises(AttributeError, self.DM.load_class, device_class, device_type)

    def test_new_device(self):
        self.fail()

    def test_remove_device(self):
        self.fail()

    def test_get_device(self):
        self.fail()

    def test_end(self):
        self.fail()

    def test_ping(self):
        self.fail()
