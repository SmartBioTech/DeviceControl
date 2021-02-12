import unittest
from unittest import mock

from sqlalchemy.exc import OperationalError

from app.models import Device, Value, Variable, VariableType, Experiment
from app.src.data_manager import DataManager
from app import create_app, db
from app.src.utils.permanent_data import VARIABLES
from app.src.utils.time import now


class DataManagerTestCases(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.DM = DataManager()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_insert(self):
        # empty
        exists = Device.query.filter_by(id='dev_id_23').first()
        self.assertIsNone(exists)

        # new device
        device = Device(id='dev_id_23', device_class='PSI', device_type='PBR')
        self.DM.insert(device, Device)
        exists = Device.query.filter_by(id='dev_id_23').first()
        self.assertIsNotNone(exists)

        # not all required attributes
        device = Device(id='dev_id_wrong', device_class='PSI')
        self.assertRaises(OperationalError, self.DM.insert, device, Device)

    def test_update(self):
        device = Device(id='dev_id_23', device_class='PSI', device_type='PBR')
        self.DM.insert(device, Device)
        dev_from_DB = Device.query.filter_by(id='dev_id_23').first()
        self.assertIsNone(dev_from_DB.address)

        db.session.remove()

        device.address = "home"
        self.DM.update(device)
        dev_from_DB = Device.query.filter_by(id='dev_id_23').first()
        self.assertEqual(dev_from_DB.address, "home")

    def test_load_variables(self):
        # empty
        self.assertEqual(self.DM.load_variables(), [])

        # filled
        self.DM.store_permanent()
        IDs = set([value[0] for value in VARIABLES])
        self.assertEqual(set(self.DM.load_variables()), IDs)

    def test_save_value(self):
        device = Device(id='dev_id_23', device_class='PSI', device_type='PBR')
        self.DM.insert(device, Device)
        self.DM.store_permanent()

        # empty
        exists = Value.query.filter_by(id='dev_id_23').first()
        self.assertIsNone(exists)

        # new value
        value = Value(id=1, time=now(), value=23, dev_id='dev_id_23', var_id='od', attribute=1, note=None)
        self.DM.save_value(value)
        result = Value.query.filter_by(dev_id='dev_id_23').first()
        self.assertEqual(result, value)

    def test_save_variable(self):
        variable = "new_var"

        # empty
        exists = Variable.query.filter_by(id=variable).first()
        self.assertIsNone(exists)

        # new variable
        self.DM.save_variable(variable)
        variable = Variable(id=variable, type=VariableType.MEASURED, unit=None, name=None)

        result = Variable.query.filter_by(id="new_var").first()
        self.assertEqual(variable, result)

    def test_save_device(self):
        connector = mock.Mock(device_id='dev_id', device_class='PSI', device_type='PBR', address='home')
        device = Device(id=connector.device_id, device_class=connector.device_class,
                        device_type=connector.device_type, address=connector.address)
        self.DM.save_experiment = mock.Mock()

        # empty
        exists = Device.query.filter_by(id=connector.device_id).first()
        self.assertIsNone(exists)

        # new device
        self.DM.save_device(connector)
        result = Device.query.filter_by(id=connector.device_id).first()
        self.assertEqual(result, device)

    def test_save_experiment(self):
        dev_id = 'dev_id_01'
        device = Device(id=dev_id, device_class='PSI', device_type='PBR', address='home')
        self.DM.insert(device, Device)

        current_time = now()
        experiment = Experiment(id=1, dev_id=dev_id, start=current_time, description=None, end=None)

        # empty
        exists = Experiment.query.filter_by(dev_id=dev_id).first()
        self.assertIsNone(exists)

        # new experiment
        self.DM.save_experiment(dev_id, current_time)
        result = Experiment.query.filter_by(dev_id=dev_id).first()
        self.assertEqual(result, experiment)

    def test_update_experiment(self):
        pass