import unittest
import time
from datetime import datetime


from app import create_app, db, app_manager


class IntegrationTestCases(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.client = self.app.test_client()
        app_manager.dataManager.store_permanent()

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
                            'task_class': 'PSI',
                            'task_type': 'PBR_pump',
                            'device_id': PBR_id,
                            'min_od': 0.4,
                            'max_od': 0.6,
                            'pump_id': 5,
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
        
        response = self.client.post('http://localhost:5000/end', json={'type': 'task', 'target_id': measure_all_task_id_2})
        self.assertTrue(response.json["success"])
        
        response = self.client.post('http://localhost:5000/end', json={'type': 'device', 'target_id': PBR_id_2})
        self.assertTrue(response.json["success"])
        
        time.sleep(10)
        
        # PBR 1
        
        response = self.client.post('http://localhost:5000/end', json={'type': 'task', 'target_id': pump_task_id})
        self.assertTrue(response.json["success"])
        
        response = self.client.post('http://localhost:5000/end', json={'type': 'task', 'target_id': measure_all_task_id})
        self.assertTrue(response.json["success"])
        
        response = self.client.post('http://localhost:5000/end', json={'type': 'device', 'target_id': PBR_id})
        self.assertTrue(response.json["success"])