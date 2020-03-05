from device_module.device_connector.PSI_java.java_device import JavaDevice
from device_module.configuration import DeviceConfig


class GMS(JavaDevice):
    def __init__(self, config: DeviceConfig):
        super(GMS, self).__init__(config.device_id,
                                  config.host_address,
                                  "device_connector/PSI_java/lib/config/device_GMS.config")
        self.interpreter = {
            1: self.get_valve_info,
            2: self.get_valve_flow,
            3: self.set_valve_flow,
        }

    def get_valve_flow(self, valve):
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
            "warning": msg.getBoolParam(2)
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

    def get_valve_info(self, valve):
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
            "user_gas_type": msg.getIntParam(2)
        }

    def test_connection(self) -> bool:
        try:
            self.get_valve_flow(0)
            return True
        except Exception:
            return False
