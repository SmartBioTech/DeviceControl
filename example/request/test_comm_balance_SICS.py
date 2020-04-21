import requests as r
from time import sleep

dev = {
    "device_id": "BAL29",
    "device_class": "MettlerToledo_SICS",
    "address": "/dev/ttyUSB0" }
r.post("http://localhost:5000/device", json=dev)

cmd = {
    "device_id": "BAL29",
    "command_id": "1",
    "source": "external" }
r.post("http://localhost:5000/command", json=cmd)

cmd = {
    "device_id": "BAL29",
    "command_id": "2",
    "source": "external" } 
r.post("http://localhost:5000/command", json=cmd)

task = { 
    "task_id": "test3",
    "task_class": "Balance_measure_weight",
    "device_id": "BAL29",
    "sleep_period": 60 }
r.post("http://localhost:5000/task", json=task)

sleep(600)

end = {
    "type": "task",
     "target_id": "test3" }
r.post("http://localhost:5000/end", json=end)