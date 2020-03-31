from threading import Thread
from time import sleep

from core.device.manager import DeviceManager
from core.manager import AppManager
from core.task.manager import TaskManager

deviceManager = DeviceManager()
taskManager = TaskManager()
appManager = AppManager(taskManager, deviceManager)

default = "flask_server"

config_pbr = {"device_id": "001",
              "device_class": "PSI_java_PBR",
              "address": "/dev/ttyUSB0"
              }

config_gas = {"device_id": "002",
              "device_class": "PSI_java_GAS",
              "address": "/dev/ttyUSB1"
              }

tasks = [config_pbr, config_gas]
for task in tasks:
    appManager.register_device(task)

sleep(10)
print(appManager.ping())