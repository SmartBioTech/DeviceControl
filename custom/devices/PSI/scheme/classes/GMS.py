from core.device_module.device_connector.abstract.device import Device
from custom.devices.PSI.scheme.scheme.command import Command
from custom.devices.PSI.scheme.scheme.scheme_manager import SchemeManager


class GMS(Device):
    def __init__(self, config):
        super(GMS, self).__init__(config)
        self._GAS_TYPES = ["CO2", "Air", "N2"]

        self._scheme_manager = SchemeManager(self.device_id, self.address)

        self.interpreter = {
            1: self.get_valve_info,
            2: self.get_valve_flow,
            3: self.set_valve_flow,
        }

    def get_valve_flow(self, valve: int) -> dict:
        """
        Get value (L/min) of current flow in the given valve.

        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :return: The current settings of the valve flow and actual value, both in (L/min).
        """
        values = ["current", "set"]
        command = Command("get-valve-flow", [valve])
        results = self._scheme_manager.execute([command])[0].rstrip()[1:-1].split()
        return dict(zip(values, list(map(float, results[1:-1]))))

    def set_valve_flow(self, valve: int, value: float) -> bool:
        """
        Set value (L/min) of current flow in the given valve.

        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :param value: desired value for valve flow in (L/min).
        :return: True if was successful, False otherwise.
        """
        command = Command("set-valve-tflow", [valve, value])
        result = self._scheme_manager.execute([command])[0].rstrip()
        return result == 'ok'

    def get_valve_info(self, valve: int) -> dict:
        """
        Gives information about the valve

        :param valve: ID of the valve (0 for CO2, 1 for Air)
        :return: A dictionary with gas type and maximal allowed flow.
        """
        values = ["max_flow", "gas_type"]
        command = Command("get-valve-info", [valve])
        results = self._scheme_manager.execute([command])[0].rstrip()[1:-1].split()
        return dict(zip(values, [float(results[1]), self._GAS_TYPES[int(results[3])]]))

    def test_connection(self) -> bool:
        try:
            self.get_valve_flow(0)
            return True
        except Exception:
            return False

    def disconnect(self) -> None:
        pass
