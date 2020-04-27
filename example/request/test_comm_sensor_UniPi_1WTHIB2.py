import requests as r
from time import sleep

dev = {
    "device_id": "264F3C4C02000028",
    "device_class": "UniPi_1WTHIB2",
    "address": "localhost" }
r.post("http://localhost:5000/device", json=dev)

cmd = {
    "device_id": "264F3C4C02000028",
    "command_id": "1",
    "arguments": "['F']",
    "source": "external" }
r.post("http://localhost:5000/command", json=cmd)

cmd = {
    "device_id": "264F3C4C02000028",
    "command_id": "3",
    "source": "external" } 
r.post("http://localhost:5000/command", json=cmd)

task = { 
    "task_id": "test2",
    "task_class": "TH_IB2_measure_all",
    "device_id": "264F3C4C02000028",
    "sleep_period": 60 }
r.post("http://localhost:5000/task", json=task)

sleep(600)

end = {
    "type": "task",
     "target_id": "test1" }
r.post("http://localhost:5000/end", json=end)