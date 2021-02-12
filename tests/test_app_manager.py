import unittest
from unittest import mock
from flask import current_app
from app import create_app, db, app_manager
from app.src.utils.response import Response


class BasicsTestCase(unittest.TestCase):
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
