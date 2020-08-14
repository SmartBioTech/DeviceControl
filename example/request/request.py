import requests

data = {"device_id": "002", "device_class": "PSI_java_GAS", "address": "/dev/ttyUSB1"}
r = requests.get("http://localhost:5000/data?device_id=D1&time=20200515005056")
print(type(r.json()))
print((r.json()))
print(type(r.text))
print(r.text)
