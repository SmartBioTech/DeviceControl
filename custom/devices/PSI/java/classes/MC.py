from custom.devices.PSI.java.abstract.java_device import JavaDevice


class MC(JavaDevice):
    def __init__(self, config: dict):
        super(MC, self).__init__(config, "custom/devices/PSI/java/lib/config/device_MC.config")
        self.interpreter = {
            "1": self.get_info,
            "9": self.measure_all,
            "10": self.get_valve_info,
            "11": self.get_valve_flow,
            "12": self.set_valve_flow,
            "13": self.get_device_type,
            "14": self.get_device_id,
            "15": self.get_serial_nr,
            "16": self.get_fw_ver
        }

    def get_info(self):
        msg = self.device.send("who")
        if msg.isError():
            raise Exception(msg.getError())
        info = {}
        info['model'] = msg.getParam(0)
        msg = self.device.send("get-hw-config")
        if msg.isError():
            raise Exception(msg.getError())
        info['model-type'] = msg.getParam(0)
        msg = self.device.send("get-serial-nr")
        if msg.isError():
            raise Exception(msg.getError())
        info['sn'] = msg.getIntParam(0)
        msg = self.device.send("get-fw-version")
        if msg.isError():
            raise Exception(msg.getError())
        info['fw'] = msg.getParam(0)
        msg = self.device.send("get-build-nr")
        if msg.isError():
            raise Exception(msg.getError())
        info['fw-build'] = msg.getIntParam(0)
        msg = self.device.send("get-device-id")
        if msg.isError():
            raise Exception(msg.getError())
        info['id'] = msg.getIntParam(0)
        return True, info

    def get_device_type(self):
        msg = self.device.send("who")
        if msg.isError():
            raise Exception(msg.getError())

        return True, {
            "type": msg.getParam(0)
        }

    def get_device_id(self):
        msg = self.device.send("get-device-id")
        if msg.isError():
            raise Exception(msg.getError())

        return True, {
            "sn": msg.getIntParam(0)
        }

    def get_serial_nr(self):
        msg = self.device.send("get-serial-nr")
        if msg.isError():
            raise Exception(msg.getError())

        return True, {
            "sn": msg.getIntParam(0)
        }

    def get_fw_ver(self):
        msg = self.device.send("get-fw-version")
        if msg.isError():
            raise Exception(msg.getError())

        return True, {
            "fw": msg.getParam(0)
        }

    def get_temp(self)
        """
        Measure temperature of the waterbath in Celsius degree.
        :return: The current temperature.
        """

        msg = self.device.send("get-tr-temp")
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)

    def get_od(self, channel=0, led=0, repeats=5):
        """
        Measure OD of all positions.
        :param channel: ID of the valve (0 for CO2, 1 for Air)
        :param led: 
        :param repeats: 
        :return: The current settings of the valve flow and actual value, both in (L/min).
        """

        msg = self.device.send("measure-od", channel, led, repeats)
        if msg.isError():
            raise Exception(msg.getError())

        return True, {
            "valve_flow_current": msg.getDoubleParam(0),
            "valve_flow_set": msg.getDoubleParam(1),
            "warning": msg.getBoolParam(2)
        }

    def measure_all(self):
        """
        Measures all basic measurable values.
        :param ft_channel: channel for ft_measure
        :param pump_id: id of particular pump
        :return: dictionary of all measured values
        """

    measure_all_dict = dict()
    try:
        measure_all_dict["temp"] = True, self.get_temp()
    except Exception:
        measure_all_dict["temp"] = False, "Cannot get temperature"

    return measure_all_dict

    def test_connection(self) -> bool:
        try:
            self.get_temp()
            return True
        except Exception:
            return False
