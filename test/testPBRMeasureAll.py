import json

from device_module.device import DeviceManager
from task_module.task_manager import TaskManager

device_config = json.load(open("device.json"))

task_config = json.load(open("task.json"))
task_config_2 = json.load(open("tasky.json"))

deviceManager = DeviceManager()
device = deviceManager.new_device(device_config)
print(device)

taskManager = TaskManager()
task = taskManager.create_task(task_config)

task2 = taskManager.create_task(task_config_2)

task.start()
task2.start()
