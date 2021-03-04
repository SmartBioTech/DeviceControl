import requests as r
from time import sleep

dev = {
    "device_id": "PBR01",
    "device_class": "test_PBR",
    "address": "home"
}
r.post("http://localhost:5000/device", json=dev)

task = {
    "task_id": "task_measure",
    "task_class": "PBR_measure_all",
    "device_id": "PBR01",
    "sleep_period": 5,
    "max_outliers": 5,
    "pump_id": 5,
    "lower_tol": 5,
    "upper_tol": 5,
    "od_channel": 1,
    "ft_channel": 0
}
r.post("http://localhost:5000/task", json=task)

task = {
    "task_id": "001DayNightRegime",
    "task_class": "PBR_day_night_regime",
    "device_id": "PBR01",
    "intervals": [10, 5, 15],
    "lights": [400, 25, 200]
}
r.post("http://localhost:5000/task", json=task)

sleep(60)

end = {
    "type": "task",
    "target_id": "001DayNightRegime"}
r.post("http://localhost:5000/end", json=end)

end = {
    "type": "task",
    "target_id": "task_measure"}
r.post("http://localhost:5000/end", json=end)

end = {
    "type": "device",
    "target_id": "PBR01"}
r.post("http://localhost:5000/end", json=end)
