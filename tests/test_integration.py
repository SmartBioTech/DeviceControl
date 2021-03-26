import unittest
import time
from datetime import datetime

from app import create_app, db, app_manager


class IntegrationTestCases(unittest.TestCase):
    def setUp(self):
        time.sleep(3)
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.client = self.app.test_client()
        app_manager.dataManager.store_permanent()
        app_manager.dataManager.last_seen_id = {'values': {}, 'events': {}}

    def tearDown(self):
        app_manager.end()
        time.sleep(2)
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_integration(self):
        ############################################################################
        ############################# start a device ###############################
        ############################################################################

        PBR_id = 'PBR-PSI-test01'
        test_PBR_device = {
            'device_id': PBR_id,
            'device_class': 'test',
            'device_type': 'PBR',
            'address': 'null',
        }

        response = self.client.post('http://localhost:5000/device', json=test_PBR_device)
        self.assertTrue(response.json["success"])

        ############################################################################
        ########################## start measure task ##############################
        ############################################################################

        # settings for periodical measurement task
        measure_all_task_id = 'task-measure-PBR-test-01'
        measure_all_task = {
            'task_id': measure_all_task_id,
            'task_class': 'PSI',
            'task_type': 'PBR_measure_all',
            'device_id': PBR_id,
            'sleep_period': 0.01,
            'max_outliers': 6,
            'pump_id': 5,
            'lower_tol': 5,
            'upper_tol': 5,
            'od_attribute': 1
        }

        response = self.client.post('http://localhost:5000/task', json=measure_all_task)
        self.assertTrue(response.json["success"])

        ############################################################################
        ############################ start turbidostat #############################
        ############################################################################

        # settings for turbidostat task
        pump_task_id = 'task-turbidostat-PBR-test-01'
        turbidostat_task = {
            'task_id': pump_task_id,
            'task_class': 'General',
            'task_type': 'PBR_general_pump',
            'device_id': PBR_id,
            'min_od': 0.4,
            'max_od': 0.6,
            'measure_all_task_id': measure_all_task_id,
            'pump_on_command': {'command_id': '8', 'arguments': '[5, True]'},
            'pump_off_command': {'command_id': '8', 'arguments': '[5, False]'}
        }

        response = self.client.post('http://localhost:5000/task', json=turbidostat_task)
        self.assertTrue(response.json["success"])

        # sleep for some time
        time.sleep(2)

        ############################################################################
        ############################## send a command ##############################
        ############################################################################

        # send a random command - to change some value
        cmd = {'device_id': PBR_id,
               'command_id': '3',
               'arguments': '[30]'
               }
        response = self.client.post('http://localhost:5000/command', json=cmd)
        self.assertTrue(response.json["success"])
        self.assertIsNone(response.json["data"])

        cmd = {'device_id': PBR_id,
               'command_id': '2',
               'await': True
               }

        response = self.client.post('http://localhost:5000/command', json=cmd)
        self.assertTrue(response.json["success"])
        self.assertEqual(response.json["data"], {'temp': 25})

        ############################################################################
        ############################## get all values ##############################
        ############################################################################

        # ask for all values
        response = self.client.get('http://localhost:5000/data?device_id={}&type=values'.format(PBR_id))
        self.assertTrue(response.json["success"])
        self.assertTrue(len(response.json["data"]) != 0)

        values_keys_first = set(map(int, response.json["data"]))

        # sleep for some more time
        time.sleep(20)

        ############################################################################
        ############################## get all events ##############################
        ############################################################################

        # ask for all events
        all_events = {'device_id': PBR_id,
                      'type': 'events'}
        response = self.client.get('http://localhost:5000/data?device_id={}&type=events'.format(PBR_id))
        self.assertTrue(response.json["success"])
        self.assertTrue(len(response.json["data"]) != 0)

        ############################################################################
        ######################## get values from a log ID ##########################
        ############################################################################

        # ask again with new log_id to check if got only new ones
        last = max(values_keys_first)
        URL = 'http://localhost:5000/data?device_id={}&type=values&log_id={}'
        response = self.client.get(URL.format(PBR_id, last))
        self.assertTrue(response.json["success"])
        self.assertTrue(len(response.json["data"]) != 0)

        values_keys_second = set(map(int, response.json["data"]))
        # check if intersection is empty
        self.assertTrue(values_keys_first & values_keys_second == set())
        # and check all values are newest than the last one
        self.assertTrue(all(list(map(lambda item: item > last, values_keys_second))))

        ############################################################################
        ###################### get values from a time point ########################
        ############################################################################

        # get data from a time point
        from_time = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        time.sleep(15)
        URL = 'http://localhost:5000/data?device_id={}&type=values&time={}'
        response = self.client.get(URL.format(PBR_id, from_time))
        self.assertTrue(response.json["success"])
        self.assertTrue(len(response.json["data"]) != 0)

        ############################################################################
        ####################### another parallel experiment ########################
        ############################################################################

        # settings for test PBR 2
        PBR_id_2 = 'PBR-PSI-test02'
        test_PBR_device['device_id'] = PBR_id_2

        response = self.client.post('http://localhost:5000/device', json=test_PBR_device)
        self.assertTrue(response.json["success"])

        # measure all for PBR 2
        measure_all_task_id_2 = 'task-measure-PBR-test-02'
        measure_all_task['task_id'] = measure_all_task_id_2
        measure_all_task['device_id'] = PBR_id_2

        response = self.client.post('http://localhost:5000/task', json=measure_all_task)
        self.assertTrue(response.json["success"])

        # turbidostat for PBR 2

        pump_task_id_2 = 'task-turbidostat-PBR-test-02'
        turbidostat_task['task_id'] = pump_task_id_2
        turbidostat_task['device_id'] = PBR_id_2
        turbidostat_task['measure_all_task_id'] = measure_all_task_id_2

        response = self.client.post('http://localhost:5000/task', json=turbidostat_task)
        self.assertTrue(response.json["success"])

        time.sleep(30)

        ############################################################################
        ########################### end tasks and device ###########################
        ############################################################################

        # PBR 2

        response = self.client.post('http://localhost:5000/end', json={'type': 'task', 'target_id': pump_task_id_2})
        self.assertTrue(response.json["success"])

        response = self.client.post('http://localhost:5000/end',
                                    json={'type': 'task', 'target_id': measure_all_task_id_2})
        self.assertTrue(response.json["success"])

        response = self.client.post('http://localhost:5000/end', json={'type': 'device', 'target_id': PBR_id_2})
        self.assertTrue(response.json["success"])

        time.sleep(10)

        # PBR 1

        response = self.client.post('http://localhost:5000/end', json={'type': 'task', 'target_id': pump_task_id})
        self.assertTrue(response.json["success"])

        response = self.client.post('http://localhost:5000/end',
                                    json={'type': 'task', 'target_id': measure_all_task_id})
        self.assertTrue(response.json["success"])

        response = self.client.post('http://localhost:5000/end', json={'type': 'device', 'target_id': PBR_id})
        self.assertTrue(response.json["success"])

    def test_integration_desync(self):
        ############################################################################
        ############################# start a device ###############################
        ############################################################################

        PBR_id = 'PBR-PSI-test01'
        test_PBR_device = {
            'device_id': PBR_id,
            'device_class': 'test',
            'device_type': 'PBR',
            'address': 'null',
        }

        response = self.client.post('http://localhost:5000/device', json=test_PBR_device)
        self.assertTrue(response.json["success"])

        ############################################################################
        ###################### start desync measure task ###########################
        ############################################################################

        frequency_to_commands = {
            10: {"o2": {"id": "14"}},
            6: {"ph": {"id": "4", "args": [5, 0]}, "light_1": {"id": "9", "args": [1]}},
            2: {"od_0": {"id": "5", "args": [0, 30]}}
        }

        measure_all_task_id = 'task-measure-PBR-test-01'
        measure_all_desync_task = {
            "task_id": measure_all_task_id,
            'task_class': 'General',
            'task_type': 'measure_all_desync',
            "device_id": PBR_id,
            "frequency_to_commands": frequency_to_commands}

        response = self.client.post('http://localhost:5000/task', json=measure_all_desync_task)
        self.assertTrue(response.json["success"])

        time.sleep(10)

        ############################################################################
        ######################### check content of DB ##############################
        ############################################################################

        # ask for all values
        response = self.client.get('http://localhost:5000/data?device_id={}&type=values'.format(PBR_id))
        self.assertTrue(response.json["success"])
        self.assertTrue(len(response.json["data"]) != 0)

        data = response.json["data"]

        o2_count = len(list(filter(lambda item: item['var_id'] == 'o2', data.values())))
        pH_count = len(list(filter(lambda item: item['var_id'] == 'pH', data.values())))
        od_count = len(list(filter(lambda item: item['var_id'] == 'od', data.values())))

        self.assertEqual(o2_count, 1)
        self.assertEqual(pH_count, 2)
        self.assertTrue(4 <= od_count <= 6)

        ############################################################################
        ########################### end task and device ############################
        ############################################################################

        response = self.client.post('http://localhost:5000/end',
                                    json={'type': 'task', 'target_id': measure_all_task_id})
        self.assertTrue(response.json["success"])

        response = self.client.post('http://localhost:5000/end', json={'type': 'device', 'target_id': PBR_id})
        self.assertTrue(response.json["success"])

    def test_regime(self):
        ############################################################################
        ############################# start a device ###############################
        ############################################################################

        PBR_id = 'PBR-PSI-test01'
        test_PBR_device = {
            'device_id': PBR_id,
            'device_class': 'test',
            'device_type': 'PBR',
            'address': 'null',
        }

        response = self.client.post('http://localhost:5000/device', json=test_PBR_device)
        self.assertTrue(response.json["success"])

        ############################################################################
        ########################## start measure task ##############################
        ############################################################################

        # settings for periodical measurement task
        measure_all_task_id = 'task-measure-PBR-test-01'
        measure_all_task = {
            'task_id': measure_all_task_id,
            'task_class': 'PSI',
            'task_type': 'PBR_measure_all',
            'device_id': PBR_id,
            'sleep_period': 1,
            'max_outliers': 6,
            'pump_id': 5,
            'lower_tol': 5,
            'upper_tol': 5,
            'od_attribute': 1
        }

        response = self.client.post('http://localhost:5000/task', json=measure_all_task)
        self.assertTrue(response.json["success"])

        ############################################################################
        ########################## start regime tasks ##############################
        ############################################################################

        light_regime_task_id = '001DayNightRegime'
        light_regime_task = {
            'task_id': light_regime_task_id,
            'task_class': 'General',
            'task_type': 'periodic_regime',
            'device_id': PBR_id,
            'intervals': [8 / 3600, 16 / 3600],  # to use seconds instead of hours
            'commands': [[{'id': '10', 'args': [0, 20]}, {'id': '10', 'args': [1, 20]}],  # night
                         [{'id': '10', 'args': [0, 200]}, {'id': '10', 'args': [1, 200]}]]  # day
        }

        response = self.client.post('http://localhost:5000/task', json=light_regime_task)
        self.assertTrue(response.json["success"])

        time.sleep(30)

        ############################################################################
        ####################### check for light changes ############################
        ############################################################################

        # ask for all values
        response = self.client.get('http://localhost:5000/data?device_id={}&type=values'.format(PBR_id))
        self.assertTrue(response.json["success"])
        self.assertTrue(len(response.json["data"]) != 0)

        data = response.json["data"]
        light_data = list(filter(lambda item: item['var_id'] == 'light_intensity', data.values()))

        middle = [light_data[len(light_data) // 2 - 1]['value'],
                  light_data[len(light_data) // 2]['value'],
                  light_data[len(light_data) // 2 + 1]['value']]

        self.assertEqual(light_data[0]['value'], 20)
        self.assertIn(200, middle)
        self.assertEqual(light_data[-1]['value'], 20)

        light_data_20 = len(list(filter(lambda item: item['value'] == 20, data.values()))) // 2
        light_data_200 = len(list(filter(lambda item: item['value'] == 200, data.values()))) // 2

        self.assertTrue(10 < light_data_20 < 20)
        self.assertTrue(10 < light_data_200 < 20)

        ############################################################################
        ########################### end tasks and device ###########################
        ############################################################################

        response = self.client.post('http://localhost:5000/end',
                                    json={'type': 'task', 'target_id': measure_all_task_id})
        self.assertTrue(response.json["success"])

        response = self.client.post('http://localhost:5000/end',
                                    json={'type': 'task', 'target_id': light_regime_task_id})
        self.assertTrue(response.json["success"])

        response = self.client.post('http://localhost:5000/end', json={'type': 'device', 'target_id': PBR_id})
        self.assertTrue(response.json["success"])
