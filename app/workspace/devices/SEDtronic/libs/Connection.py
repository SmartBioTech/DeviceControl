import requests


class Connection:
    def __init__(self, address, port, device_id):
        self.port = port
        self.address = address
        self.port = port
        self.device_id = device_id

    def read_sensor(self):
        return requests.get('http://' + self.address + ':' + self.port + '/rest/sensor/' + self.device_id), \
               requests.codes
