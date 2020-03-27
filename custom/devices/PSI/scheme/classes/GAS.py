from core.device_module.device_connector.abstract.device import Device
from custom.devices.PSI.scheme.libs.parsing import Parser
from custom.devices.PSI.scheme.scheme.command import Command
from custom.devices.PSI.scheme.scheme.scheme_manager import SchemeManager


class GAS(Device):
    def __init__(self, config):
        super(GAS, self).__init__(config)
        self._parser = Parser()

        self._scheme_manager = SchemeManager(self.device_id, self.address)
        self.interpreter = {
            1: self.get_flow,
            2: self.get_flow_target,
            3: self.set_flow_target,
            4: self.get_flow_max,
            5: self.get_pressure,
            6: self.measure_all,
            7: self.get_co2_air,
            8: self.get_small_valves,
            9: self.set_small_valves,
        }

    def get_co2_air(self) -> float:
        """
        Measures CO2 in air.

        :return: measured CO2 in air
        """
        command = Command("get-co2-air")
        value = self._scheme_manager.execute([command])
        return self._parser.parse_co2_air(value)

    def get_small_valves(self) -> str:
        """
        Obtain settings of individual vents of GAS device_module.

        Represented as one byte, where first 6 bits represent
        vents indexed as in a picture scheme available here:
        https://i.imgur.com/jSeFFaO.jpg

        :return: byte representation of vents settings.
        """
        command = Command("get-small-valves")
        value = self._scheme_manager.execute([command])
        return self._parser.parse_small_valves(value)

    def set_small_valves(self, mode: int) -> bool:
        """
        Changes settings of individual vents of GAS device_module.

        Can be set by one byte (converted to int), where first 6
        bits represent vents indexed as in a picture scheme
        available here: https://i.imgur.com/jSeFFaO.jpg

        Mode 0 - normal mode, output from GMS goes to PBR (255)
        Mode 1 - reset mode, N2 (nitrogen) goes to PBR (239)
        Mode 2 - no gas input to PBR (249)
        Mode 3 - output of PBR goes to input of PBR (246)

        :param mode: chosen mode (0 to 3)
        :return: True if was successful, False otherwise.
        """
        modes = {0: "11111111", 1: "11101111", 2: "11111001", 3: "11110110"}
        command = Command("get-small-valves", [int(modes[mode], 2)])
        result = self._scheme_manager.execute([command])[0].rstrip()
        return result == 'ok'

    def get_flow(self, repeats: int) -> float:
        """
        Actual flow being send from GAS to the PBR.

        :param repeats: the number of measurement repeats
        :return: The current flow in L/min.
        """
        command = Command("get-flow", [repeats])
        value = self._scheme_manager.execute([command])
        return self._parser.parse_flow(value)

    def get_flow_target(self) -> float:
        """
        Actual desired flow.

        :return: The desired flow in L/min.
        """
        command = Command("get-flow-target")
        value = self._scheme_manager.execute([command])
        return self._parser.parse_flow_target(value)

    def set_flow_target(self, flow: float) -> bool:
        """
        Set flow we want to achieve.

        :param flow: flow in L/min we want to achieve (max given by get_flow_max)
        :return: True if was successful, False otherwise.
        """
        command = Command("set-flow-target", [flow])
        result = float(self._scheme_manager.execute([command])[0].rstrip())
        return result == 'ok'

    def get_flow_max(self) -> float:
        """
        Maximal allowed flow.

        :return: The maximal flow in L/min
        """
        command = Command("get-flow-max")
        value = self._scheme_manager.execute([command])
        return self._parser.parse_flow_max(value)

    def get_pressure(self, repeats: int = 5, wait: int = 0) -> float:
        """
        Current pressure.

        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: Current pressure in ???
        """
        command = Command("get-pressure", [repeats, wait])
        value = self._scheme_manager.execute([command])
        return self._parser.parse_pressure(value)

    def measure_all(self):
        """
        Measures all basic measurable values.
        """
        commands = [Command("get-co2-air"),
                    Command("get-flow", [5]),
                    Command("get-pressure", [5, 0])]

        values = self._scheme_manager.execute(commands)

        result = dict()
        result["co2_air"] = self._parser.parse_co2_air(values[0])
        result["flow"] = self._parser.parse_flow(values[1])
        result["pressure"] = self._parser.parse_pressure(values[2])

        return result

    def test_connection(self) -> bool:
        try:
            self.get_co2_air()
            return True
        except Exception:
            return False

    def disconnect(self) -> None:
        pass
