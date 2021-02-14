import unittest
from unittest import mock

from app.src.device_manager import DeviceManager
from app import create_app, db
from app.src.utils.errors import IdError
from app.workspace.devices.PSI import test


class DataManagerTestCases(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.DM = DeviceManager()

    def tearDown(self):
        self.DM.end()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_load_class(self):
        # correct case
        device_class = 'test'
        device_type = 'PBR'

        expected_class = test.PBR
        result = self.DM.load_class(device_class, device_type)
        self.assertEqual(expected_class, result)

        # unknown class
        device_class = 'Magic'
        device_type = 'PBR'
        self.assertRaises(KeyError, self.DM.load_class, device_class, device_type)

        # unknown type
        device_class = 'PSI'
        device_type = 'Magic'
        self.assertRaises(KeyError, self.DM.load_class, device_class, device_type)

    def test_new_device(self):
        config = {"device_class": 'PSI', "device_type": 'PBR', "device_id": 'my_id_23'}
        correct_device = test.PBR(config)
        self.DM.load_class = mock.Mock(return_value=test.PBR)
        device = self.DM.new_device(config)
        self.assertEqual(correct_device, device)

        self.assertRaises(IdError, self.DM.new_device, config)
        correct_device.end()

    def test_remove_device(self):
        config = {"device_class": 'PSI', "device_type": 'PBR', "device_id": 'my_id_23'}
        device = test.PBR(config)
        self.DM._devices[config["device_id"]] = device
        self.DM.remove_device(config["device_id"])
        self.assertEqual(self.DM._devices, dict())

    def test_get_device(self):
        config = {"device_class": 'PSI', "device_type": 'PBR', "device_id": 'my_id_23'}
        device = test.PBR(config)
        self.DM._devices[config["device_id"]] = device
        self.assertEqual(self.DM.get_device(config["device_id"]), device)

        self.assertRaises(IdError, self.DM.get_device, '23')

    def test_end(self):
        config = {"device_class": 'PSI', "device_type": 'PBR', "device_id": 'my_id_23'}
        device = test.PBR(config)
        self.DM._devices[config["device_id"]] = device

        self.DM.end()
        self.assertEqual(self.DM._devices, dict())

    def test_ping(self):
        config = {"device_class": 'PSI', "device_type": 'PBR', "device_id": 'my_id_23'}
        device = test.PBR(config)
        self.DM._devices[config["device_id"]] = device

        result = {config["device_id"]: True}

        self.assertEqual(self.DM.ping(), result)
        device.end()
