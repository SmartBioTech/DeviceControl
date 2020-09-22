import requests as r
from time import sleep

dev = {
    "device_id": "PBR01",
    "device_class": "test_PBR",
    "address": "home"
}
r.post("http://localhost:5000/device", json=dev)

frequency_to_commands = {
                         10: {"o2": {"id": "14"}},
                         6: {"ph": {"id": "4", "args": [5, 0]}, "light_1": {"id": "9", "args": [1]}},
                         2: {"od_0": {"id": "5", "args": [0, 30]}}
                        }

task = {
    "task_id": "measure_desync",
    "task_class": "PBR_measure_all_desync",
    "device_id": "PBR01",
    "frequency_to_commands": frequency_to_commands}
r.post("http://localhost:5000/task", json=task)

sleep(60)

end = {
    "type": "task",
    "target_id": "measure_desync"}
r.post("http://localhost:5000/end", json=end)

end = {
    "type": "device",
    "target_id": "PBR01"}
r.post("http://localhost:5000/end", json=end)
