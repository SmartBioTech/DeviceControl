import json

import requests

device_config = json.load(open("device.json"))

task_config = json.load(open("task.json"))

'''manager = Manager()
manager.create_node(1)
device = manager.register_device(device_config)
manager.add_device_to_node(1, device)
print(device)

manager.register_task(task_config)
print(manager.ping())
print(manager.taskManager.tasks)
manager.remove_task(task_config.get("task_id"))
print(manager.taskManager.tasks)
'''

r = requests.post("http://127.0.0.1:5000/device", json=json.dumps(device_config))
print(r.text)
