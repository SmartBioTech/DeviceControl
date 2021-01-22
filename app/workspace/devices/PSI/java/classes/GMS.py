from ..abstract.java_device import JavaDevice


class GMS(JavaDevice):
    def __init__(self, config: dict):
        super(GMS, self).__init__(config, "custom/devices/PSI/java/lib/config/device_GMS.config")
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

    def get_valve_flow(self, valve=0):
        """
        Get value (L/min) of current flow in the given valve.
        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :return: The current settings of the valve flow and actual value, both in (L/min).
        """

        msg = self.device.send("get-valve-flow", valve)
        if msg.isError():
            raise Exception(msg.getError())

        return True, {
            "valve_flow_current": msg.getDoubleParam(0),
            "valve_flow_set": msg.getDoubleParam(1),
            "warning": int(msg.getBoolParam(2)),
            "channel": valve
        }

    def set_valve_flow(self, valve, value):
        """
        Set value (L/min) of current flow in the given valve.
        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :param value: desired value for valve flow in (L/min).
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-valve-flow", valve, value)
        return not msg.isError()

    def get_valve_info(self, valve=0):
        """
        Gives information about the valve
        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :return: A dictionary with gas type and maximal allowed flow.
        """

        msg = self.device.send("get-valve-info", valve)
        if msg.isError():
            raise Exception(msg.getError())

        return True, {
            "valve_max_flow": msg.getDoubleParam(0),
            "valve_gas_type": msg.getIntParam(1),
            "user_gas_type": msg.getIntParam(2),
            "channel": valve
        }

    def measure_all(self):
        """
        Gives information about the valve
        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :return: A dictionary with gas type and maximal allowed flow.
        """

        msg = self.device.send("get-valve-flow", 0)
        if msg.isError():
            raise Exception(msg.getError())
        data = {}
        data['valve-flow-0'] = msg.getDoubleParam(0)
        msg = self.device.send("get-valve-flow", 1)
        if msg.isError():
            raise Exception(msg.getError())
        data['valve-flow-1'] = msg.getDoubleParam(0)

        return True, data

    def test_connection(self) -> bool:
        try:
            self.get_valve_flow(0)
            return True
        except Exception:
            return False
