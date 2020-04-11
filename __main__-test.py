from threading import Thread
from time import sleep

from core.data.manager import DataManager
from core.device.manager import DeviceManager
from core.flow.workflow import WorkflowProvider, Job
from core.manager import AppManager
from core.task.manager import TaskManager

deviceManager = DeviceManager()
taskManager = TaskManager()
dataManager = DataManager()

appManager = AppManager(taskManager, deviceManager, dataManager)

workflowProvider = WorkflowProvider()

default = "flask_server"

config_pbr = {"device_id": "001",
              "device_class": "PSI_java_PBR",
              "address": "/dev/ttyUSB0"
              }

config_gas = {"device_id": "002",
              "device_class": "PSI_java_GAS",
              "address": "/dev/ttyUSB1"
              }

devices = [config_pbr, config_gas]
for device in devices:
    job = Job(appManager.register_device, [device])
    Thread(target=WorkflowProvider.scheduler.schedule_job, args=[job]).start()

sleep(20)

measure_all_PBR = {
    "task_id": "001measureall",
    "task_class": "PBR_measure_all",
    "device_id": "001",
    "sleep_period": 5,
    "max_outliers": 5,
    "pump_id": 1,
    "lower_tol": 5,
    "upper_tol": 5,
    "od_channel": 1,
    "ft_channel": 5
}

measure_all_GAS = {
    "task_id": "002measureall",
    "task_class": "GAS_measure_all",
    "device_id": "002",
    "sleep_period": 5
}

tasks = [measure_all_GAS, measure_all_PBR]
for task in tasks:
    job = Job(appManager.register_task(), [task])
    Thread(target=WorkflowProvider.scheduler.schedule_job, args=[job]).start()
