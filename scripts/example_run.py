import requests
import time
from datetime import datetime

ADDRESS = 'http://localhost:5000/'

###################################################
print('Starting a test device... ', end="")

PBR_id = 'PBR-PSI-test01'
test_PBR_device = {
    'device_id': PBR_id,
    'device_class': 'test',
    'device_type': 'PBR',
    'address': 'null',
}

response = requests.post('http://localhost:5000/device', json=test_PBR_device)
print(f'{"successful" if response.json()["success"] else "failed"}')
assert response.json()["success"]

###################################################
print('Starting a measurement task... ', end="")

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

response = requests.post('http://localhost:5000/task', json=measure_all_task)
print(f'{"was successful" if response.json()["success"] else "failed"}')
assert response.json()["success"]

###################################################
print('Starting a turbidostat... ', end="")

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

response = requests.post('http://localhost:5000/task', json=turbidostat_task)
print(f'{"successful" if response.json()["success"] else "failed"}')
assert response.json()["success"]

# sleep for some time
time.sleep(2)

###################################################
print('Sending a command... ', end="")

# send a random command - to change some value
cmd = {'device_id': PBR_id,
       'command_id': '3',
       'arguments': '[30]'
       }
response = requests.post('http://localhost:5000/command', json=cmd)
print(f'{"successful" if response.json()["success"] and response.json()["data"] is None else "failed"}')
assert response.json()["success"] and response.json()["data"] is None

###################################################
print('Measuring temperature... ', end="")

cmd = {'device_id': PBR_id,
       'command_id': '2',
       'await': True
       }

response = requests.post('http://localhost:5000/command', json=cmd)
if response.json()["success"]:
    print(response.json()["data"])
else:
    print('failed')
assert response.json()["success"]
assert response.json()["data"] == {'temp': 25}

###################################################
print('Get all measured values... ', end="")

# ask for all values
response = requests.get('http://localhost:5000/data?device_id={}&type=values'.format(PBR_id))
print(f'{"successful" if response.json()["success"] and len(response.json()["data"]) != 0 else "failed"}')
assert response.json()["success"] and len(response.json()["data"]) != 0

values_keys_first = set(map(int, response.json()["data"]))

# sleep for some more time
print('*Sleep for 20 seconds.*')
time.sleep(20)

###################################################
print('Check all events... ', end="")

# ask for all events
all_events = {'device_id': PBR_id,
              'type': 'events'}
response = requests.get('http://localhost:5000/data?device_id={}&type=events'.format(PBR_id))
print(f'{"successful" if response.json()["success"] and len(response.json()["data"]) != 0 else "failed"}')
assert response.json()["success"] and len(response.json()["data"]) != 0

###################################################
print('Get all unseen measured values... ', end="")

# ask again with new log_id to check if got only new ones
last = max(values_keys_first)
URL = 'http://localhost:5000/data?device_id={}&type=values&log_id={}'
response = requests.get(URL.format(PBR_id, last))
print(f'{"successful" if response.json()["success"] and len(response.json()["data"]) != 0 else "failed"}')
assert response.json()["success"] and len(response.json()["data"]) != 0

print('- Check if intersection is empty... ', end="")
values_keys_second = set(map(int, response.json()["data"]))
check = values_keys_first & values_keys_second == set()
print(f'{"successful" if check else "failed"}')
assert check

print('- Check all values are newest than the seen ones... ', end="")
check = all(list(map(lambda item: item > last, values_keys_second)))
print(f'{"successful" if check else "failed"}')
assert check

###################################################
print('Get data from a time point... ', end="")

from_time = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
print('*Sleep for 15 seconds.*')
time.sleep(15)
URL = 'http://localhost:5000/data?device_id={}&type=values&time={}'
response = requests.get(URL.format(PBR_id, from_time))
print(f'{"successful" if response.json()["success"] and len(response.json()["data"]) != 0 else "failed"}')

###################################################
print('\nStarting a parallel experiment.\n')

###################################################
print('Starting a test device... ', end="")

# settings for test PBR 2
PBR_id_2 = 'PBR-PSI-test02'
test_PBR_device['device_id'] = PBR_id_2

response = requests.post('http://localhost:5000/device', json=test_PBR_device)
print(f'{"successful" if response.json()["success"] else "failed"}')
assert response.json()["success"]

###################################################
print('Starting a measurement task... ', end="")

# measure all for PBR 2
measure_all_task_id_2 = 'task-measure-PBR-test-02'
measure_all_task['task_id'] = measure_all_task_id_2
measure_all_task['device_id'] = PBR_id_2

response = requests.post('http://localhost:5000/task', json=measure_all_task)
print(f'{"was successful" if response.json()["success"] else "failed"}')
assert response.json()["success"]

###################################################
print('Starting a turbidostat... ', end="")

pump_task_id_2 = 'task-turbidostat-PBR-test-02'
turbidostat_task['task_id'] = pump_task_id_2
turbidostat_task['device_id'] = PBR_id_2
turbidostat_task['measure_all_task_id'] = measure_all_task_id_2

response = requests.post('http://localhost:5000/task', json=turbidostat_task)
print(f'{"successful" if response.json()["success"] else "failed"}')
assert response.json()["success"]

print('*Sleep for 30 seconds.*')

time.sleep(30)

###################################################
print('\nEnding second experiment.\n')

###################################################
print('Ending turbidostat... ', end="")

response = requests.post('http://localhost:5000/end', json={'type': 'task', 'target_id': pump_task_id_2})
print(f'{"successful" if response.json()["success"] else "failed"}')
assert response.json()["success"]

###################################################
print('Ending measurement task... ', end="")

response = requests.post('http://localhost:5000/end',
                         json={'type': 'task', 'target_id': measure_all_task_id_2})
print(f'{"successful" if response.json()["success"] else "failed"}')
assert response.json()["success"]

###################################################
print('Ending device... ', end="")

response = requests.post('http://localhost:5000/end', json={'type': 'device', 'target_id': PBR_id_2})
print(f'{"successful" if response.json()["success"] else "failed"}')
assert response.json()["success"]

print('*Sleep for 10 seconds.*')
time.sleep(10)

###################################################
print('\nEnding first experiment.\n')

# PBR 1

###################################################
print('Ending turbidostat... ', end="")

response = requests.post('http://localhost:5000/end', json={'type': 'task', 'target_id': pump_task_id})
print(f'{"successful" if response.json()["success"] else "failed"}')
assert response.json()["success"]

###################################################
print('Ending measurement task... ', end="")

response = requests.post('http://localhost:5000/end',
                         json={'type': 'task', 'target_id': measure_all_task_id})
print(f'{"successful" if response.json()["success"] else "failed"}')
assert response.json()["success"]

###################################################
print('Ending device... ', end="")

response = requests.post('http://localhost:5000/end', json={'type': 'device', 'target_id': PBR_id})
print(f'{"successful" if response.json()["success"] else "failed"}')
assert response.json()["success"]

print('Run successful.')
