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
        levels = self.dev.get_mtsics_level() 
        data = self.dev.get_balance_data()
        sw = self.dev.get_software_version()
        sn = self.dev.get_serial_number()
        sw_id = self.dev.get_software_id()
        if len(data) > 3:
            info = {
                'sics-levels': levels[0],
                'model': data[0],
                'model-type': data[1],
                'capacity': data[2],
                'unit': data[3],
                'sn': sn,
                'sw-version': sw[0],
                'sw-type': sw[1],
                'sw-id': sw_id
            }
        else:
            info = {
                'sics-levels': levels[0],
                'model': data[0],
                'capacity': data[1],
                'unit': data[2]
                'sn': sn,
                'sw-version': sw[0],
                'sw-type': sw[1],
                'sw-id': sw_id
            }
        return info

    def get_address(self):
        return self.dev.get_port()

    def close(self):
        self.dev.close()
