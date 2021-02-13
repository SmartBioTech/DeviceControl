import unittest
from unittest import mock

from sqlalchemy.exc import OperationalError

from app.models import Device, Value, Variable, VariableType, Experiment
from app.src.data_manager import DataManager
from app import create_app, db
from app.src.utils.permanent_data import VARIABLES
from app.src.utils.time import now, time_to_string


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

        # get rid of objects in the session
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
        dev_id = 'dev_id_01'
        device = Device(id=dev_id, device_class='PSI', device_type='PBR', address='home')
        self.DM.insert(device, Device)
        current_time = now()
        self.DM.save_experiment(dev_id, current_time)

        # no end time
        result = Experiment.query.filter_by(dev_id=dev_id).first()
        self.assertIsNone(result.end)

        # get rid of objects in the session
        db.session.remove()

        # update experiment
        self.DM.update_experiment(dev_id)
        result = Experiment.query.filter_by(dev_id=dev_id).first()
        self.assertIsNotNone(result.end)

    def test_post_process(self):
        class Helper:
            def __init__(self, id, data):
                self.id = id
                self._sa_instance_state = id
                self.time = now()
                self.data = data

        query_results = [Helper(1, "some data 1"), Helper(2, "some data 2"),
                         Helper(3, "some data 3"), Helper(4, "some data 4")]

        correct_result = {obj.id: {'time': time_to_string(obj.time), 'data': obj.data} for obj in query_results}

        result = self.DM.post_process(query_results, 'values', None)
        self.assertEqual(correct_result, result)

    def test_get_data(self):
        # preparations
        device = Device(id='dev_id_23', device_class='PSI', device_type='PBR')
        self.DM.insert(device, Device)
        self.DM.store_permanent()
        # store some values
        values = [Value(id=1, time=now(), value=23.0, dev_id='dev_id_23', var_id='od', attribute=1, note=None),
                  Value(id=2, time=now(), value=24.0, dev_id='dev_id_23', var_id='od', attribute=1, note=None),
                  Value(id=3, time=now(), value=25.0, dev_id='dev_id_23', var_id='od', attribute=1, note=None),
                  Value(id=4, time=now(), value=26.0, dev_id='dev_id_23', var_id='od', attribute=1, note=None),
                  Value(id=5, time=now(), value=27.0, dev_id='dev_id_23', var_id='od', attribute=1, note=None)]

        for value in values:
            self.DM.save_value(value)

        # values from id
        expected_results = {obj.id: {'time': time_to_string(obj.time), 'value': obj.value, 'var_id': obj.var_id,
                                     'dev_id': obj.dev_id, 'attribute': obj.attribute, 'note': obj.note}
                            for obj in values[3:]}

        result = self.DM.get_data(3, None, device.id, 'values')
        self.assertEqual(expected_results, result)

        # values from time
        result = self.DM.get_data(None, values[2].time, device.id, 'values')
        self.assertEqual(expected_results, result)

    def test_get_latest_data(self):
        # preparations
        device = Device(id='dev_id_23', device_class='PSI', device_type='PBR')
        self.DM.insert(device, Device)
        self.DM.store_permanent()
        # store some values
        values = [Value(id=1, time=now(), value=23.0, dev_id='dev_id_23', var_id='od', attribute=1, note=None),
                  Value(id=2, time=now(), value=24.0, dev_id='dev_id_23', var_id='od', attribute=1, note=None),
                  Value(id=3, time=now(), value=25.0, dev_id='dev_id_23', var_id='od', attribute=1, note=None),
                  Value(id=4, time=now(), value=26.0, dev_id='dev_id_23', var_id='od', attribute=1, note=None),
                  Value(id=5, time=now(), value=27.0, dev_id='dev_id_23', var_id='od', attribute=1, note=None)]

        for value in values:
            self.DM.save_value(value)

        # get last value
        result = self.DM.get_latest_data(device.id, 'values')
        self.assertEqual(values[4], result)
