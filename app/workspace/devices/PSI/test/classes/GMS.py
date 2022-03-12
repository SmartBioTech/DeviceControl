from .. import Connector


class GMS(Connector):
    """
    Commands:

    - "1": self.get_info,
    - "2": self.get_valve_flow,
    - "3": self.set_valve_flow,
    """
    def __init__(self, config):
        super(GMS, self).__init__(config)
        self._GAS_TYPES = ["CO2", "Air", "N2"]

        self.interpreter = {
            "1": self.get_valve_info,
            "2": self.get_valve_flow,
            "3": self.set_valve_flow,
        }

    def get_valve_flow(self, valve):
        """
        Get value (L/min) of current flow in the given valve.

        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :return: The current settings of the valve flow and actual value, both in (L/min).
        """
        return True, {"valve_flow_current": 5, "valve_flow_set": 10, "attribute": valve}

    def set_valve_flow(self, valve, value):
        """
        Set value (L/min) of current flow in the given valve.

        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :param value: desired value for valve flow in (L/min).
        :return: True if was successful, False otherwise.
        """
        return True

    def get_valve_info(self, valve):
        """
        Gives information about the valve

        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :return: A dictionary with gas type and maximal allowed flow.
        """
        return True, {"valve_max_flow": 10, "valve_gas_type": self._GAS_TYPES[0], "attribute": valve}

    def test_connection(self) -> bool:
        return True

    def disconnect(self) -> None:
        print("Test GMS {} on {} is disconnecting".format(self.device_id, self.address))
