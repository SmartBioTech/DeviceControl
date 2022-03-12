import unittest

from sqlalchemy import exc

from app import create_app, db, app_manager
from app.command import Command
from app.models import Event


class CommandTestCases(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        dev_config = {"device_class": 'test', "device_type": 'PBR', "device_id": '2', 'address': "home"}
        app_manager.dataManager._store_permanent()
        app_manager.register_device(dev_config)

    def tearDown(self):
        app_manager.end_device('2')
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_save_command_to_db(self):
        command = Command('2', '23', [1, 2, 3], 'me', is_awaited=False)

        self.assertRaises(exc.OperationalError, command.save_command_to_db)

        command.resolve()
        command.response = 'success'

        command.save_command_to_db()
        self.assertTrue(command._saved)

    def test_save_data_to_db(self):
        command = Command('2', '23', [1, 2, 3], 'me', is_awaited=False)
        command.resolve()
        command.response = {'od': 0.4, 'outlier': False}

        # invalid command = event
        command.save_data_to_db()
        self.assertIsNotNone(Event.query.filter_by(dev_id='2').first())

        # valid command = value
        command.is_valid = True
        command.save_data_to_db()
        self.assertIsNotNone(Event.query.filter_by(dev_id='2').first())
