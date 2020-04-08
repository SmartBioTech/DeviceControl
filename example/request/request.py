import requests

data = {"device_id": "002", "device_class": "PSI_java_GAS", "address": "/dev/ttyUSB1"}
r = requests.post("http://localhost:5000/device", json=data)
print(r.status_code, r.text)
