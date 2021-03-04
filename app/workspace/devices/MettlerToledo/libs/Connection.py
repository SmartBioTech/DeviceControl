from mettler_toledo_device import MettlerToledoDevice


class Connection:
    def __init__(self, address, device_id):
        self.address = address
        self.device_id = device_id
        self.dev = MettlerToledoDevice(port=self.address)

    def get_weight(self):
        weight = self.dev.get_weight()
        return {'value': weight[0], 'unit': weight[1], 'stable': True if weight[2] == 'S' else False}

    def get_info(self):
        data = self.dev.get_balance_data()
        sn = self.dev.get_serial_number()
        sw = self.dev.get_software_version()
        if len(data) > 3:
            info = {
                'model': data[0],
                'model-type': data[1],
                'sn': sn,
                'sw-version': sw[0],
                'sw-type': sw[1],
                'capacity': data[1],
                'unit': data[2]
            }
        else:
            info = {
                'model': data[0],
                'sn': sn,
                'sw-version': sw[0],
                'sw-type': sw[1],
                'capacity': data[1],
                'unit': data[2]
            }
        return info

    def get_address(self):
        return self.dev.get_port()

    def close(self):
        self.dev.close()
