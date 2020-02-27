from device_connector.PSI_scheme.libs.parsing import Parser
from device_connector.PSI_scheme.scheme.command import Command
from device_connector.PSI_scheme.scheme.scheme_manager import SchemeManager

from device_connector.abstract.device import Device
from device_module.configuration import DeviceConfig


class PBR(Device):
    def __init__(self, config: DeviceConfig):
        super(PBR, self).__init__()
        self._parser = Parser()
        self.id = config.device_id
        self.address = config.host_address
        self._scheme_manager = SchemeManager(self.id, self.address)
        self.interpreter = {
            1: self.get_temp_settings,
            2: self.get_temp,
            3: self.set_temp,
            4: self.get_ph,
            5: self.measure_od,
            6: self.get_pump_params,
            7: self.set_pump_params,
            8: self.set_pump_state,
            9: self.get_light_intensity,
            10: self.set_light_intensity,
            11: self.turn_on_light,
            12: self.get_pwm_settings,
            13: self.set_pwm,
            14: self.get_o2,
            15: self.get_thermoregulator_settings,
            16: self.set_thermoregulator_state,
            17: self.measure_ft,
            18: self.get_co2,
            19: self.measure_all,
            20: self.measure_AUX,
            21: self.flash_LED,
            22: self.get_hardware_address,
            23: self.get_cluster_name
        }

    def get_temp_settings(self) -> dict:
        """
        Get information about currently set temperature, maximal and
        minimal allowed temperature.

        :return: The current settings structured in a dictionary.
        """
        results = ["set", "min", "max"]
        command = Command("get-thermoregulator-settings")
        value = self._scheme_manager.execute([command])
        return self._parser.parse_temp_settings(results, value)

    def get_temp(self) -> float:
        """
        Get current temperature in Celsius degree.

        :return: The current temperature.
        """
        command = Command("get-current-temperature")
        value = self._scheme_manager.execute([command])
        return self._parser.parse_temp(value)

    def set_temp(self, temp: float) -> bool:
        """
        Set desired temperature in Celsius degree.

        :param temp: The temperature.
        :return: True if was successful, False otherwise.
        """
        command = Command("set-thermoregulator-temp", [temp])
        return self._scheme_manager.execute([command])[0].rstrip() == 'ok'

    def get_ph(self, repeats: int = 5, wait: int = 0) -> float:
        """
        Get current pH (dimensionless.)

        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: The current pH.
        """
        command = Command("get-ph", [repeats, wait])
        value = self._scheme_manager.execute([command])
        return self._parser.parse_ph(value)

    def measure_od(self, channel: int = 0, repeats: int = 30) -> float:
        """
        Measure current Optical Density (OD, dimensionless).

        :param channel: which channel should be measured
        :param repeats: the number of measurement repeats
        :return: Measured OD
        """
        command = Command("measure-od", [channel, repeats])
        value = self._scheme_manager.execute([command])
        return self._parser.parse_od(value)

    def get_pump_params(self, pump: int) -> dict:
        """
        Get parameters for given pump.

        :param pump: Given pump
        :return: The current settings structured in a dictionary.
        """
        command = Command("get-pump-info", [pump])
        value = self._scheme_manager.execute([command])
        return self._parser.parse_pump_params(value)

    def set_pump_params(self, pump: int, direction: int, flow: float) -> bool:
        """
        Set up the rotation direction and flow for given pump.

        :param pump: Given pump
        :param direction: Rotation direction (1 right, -1 left)
        :param flow: Desired flow rate
        :return:  True if was successful, False otherwise.
        """
        command = Command("set-pump-params", [pump, direction, flow])
        return self._scheme_manager.execute([command])[0].rstrip() == 'ok'

    def set_pump_state(self, pump: int, on: bool) -> bool:
        """
        Turns on/off given pump.

        :param pump: ID of a pump
        :param on: True to turn on, False to turn off
        :return: True if was successful, False otherwise.
        """
        command = Command("set-pump-state", [pump, self._scheme_manager.to_scheme_bool(on)])
        return self._scheme_manager.execute([command])[0].rstrip() == 'ok'

    def get_light_intensity(self, channel: int) -> dict:
        """
        Checks for current (max?) light intensity.

        Items: "intensity": current light intensity (float) in μE,
               "max": maximal intensity (float) in μE,
               "on": True if light is turned on (bool)

        :param channel: Given channel ID
        :return: The current settings structured in a dictionary.
        """
        command = Command("get-actinic-continual-settings", [channel])
        value = self._scheme_manager.execute([command])
        return self._parser.parse_light_intensity(value)

    def set_light_intensity(self, channel: int, intensity: float) -> bool:
        """
        Control LED panel on photobioreactor.

        :param channel: Given channel (0 for red light, 1 for blue light)
        :param intensity: Desired intensity
        :return: True if was successful, False otherwise.
        """
        command = Command("set-actinic-continual-intensity", [channel, intensity])
        return self._scheme_manager.execute([command])[0].rstrip() == 'ok'

    def turn_on_light(self, channel: int, on: bool) -> bool:
        """
        Turn on/off LED panel on photobioreactor.

        :param channel: Given channel
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        command = Command("set-actinic-continual-mode", [channel, self._scheme_manager.to_scheme_bool(on)])
        return self._scheme_manager.execute([command])[0].rstrip() == 'ok'

    def get_pwm_settings(self) -> dict:
        """
        Checks for current stirring settings.

        Items: "pulse": current stirring in %,
               "min": minimal stirring in %,
               "max": maximal stirring in %,
               "on": True if stirring is turned on (bool)

        :return: The current settings structured in a dictionary.
        """
        command = Command("get-pwm-settings")
        value = self._scheme_manager.execute([command])
        return self._parser.parse_pwm_settings(value)

    def set_pwm(self, value: int, on: bool) -> bool:
        """
        Set stirring settings.
        Channel: 0 red and 1 blue according to PBR configuration.

        :param value: desired stirring pulse
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        command = Command("set-pwm", [value, self._scheme_manager.to_scheme_bool(on)])
        return self._scheme_manager.execute([command])[0].rstrip() == 'ok'

    def get_o2(self, raw: bool = True, repeats: int = 5, wait: int = 0) -> float:
        """
        Checks for concentration of dissociated O2.

        Items: "pulse": current stirring in %,
               "min": minimal stirring in %,
               "max": maximal stirring in %,
               "on": True if stirring is turned on (bool)

        :param raw: True for raw data, False for data calculated according to temperature calibration
        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: The current settings structured in a dictionary.
        """
        command = Command("get-o2/h2", [repeats, wait, self._scheme_manager.to_scheme_bool(raw)])
        value = self._scheme_manager.execute([command])
        return self._parser.parse_o2(value)

    def get_thermoregulator_settings(self) -> dict:
        """
        Get current settings of thermoregulator.

        Items: "temp": current temperature in Celsius degrees,
               "min": minimal allowed temperature,
               "max": maximal allowed temperature,
               "on": state of thermoregulator (1 -> on, 0 -> freeze, -1 -> off)

        :return: The current settings structured in a dictionary.
        """
        command = Command("get-thermoregulator-settings")
        value = self._scheme_manager.execute([command])
        return self._parser.parse_thermoregulator_settings(value)

    def set_thermoregulator_state(self, on: int) -> bool:
        """
        Set state of thermoregulator.

        :param on: 1 -> on, 0 -> freeze, -1 -> off
        :return: True if was successful, False otherwise.
        """
        command = Command("set-thermoregulator-state", [on])
        return self._scheme_manager.execute([command])[0].rstrip() == 'ok'

    def measure_ft(self, channel: int) -> float:
        """
        ???

        :param channel: ???
        :return: ???
        """
        command = Command("measure-ft", [channel])
        value = self._scheme_manager.execute([command])
        return self._parser.parse_ft(value)

    def get_co2(self, raw: bool = True, repeats: int = 5) -> float:
        """
        TBA

        :param raw: True for raw data, False for data ???
        :param repeats: the number of measurement repeats
        :return:
        """
        command = Command("get-co2", [repeats, self._scheme_manager.to_scheme_bool(raw)])
        value = self._scheme_manager.execute([command])
        return self._parser.parse_co2(value)

    def measure_all(self, channel=5):
        """
        Measures all basic measurable values.

        channel for measure-ft ???
        need to solve the case when one of the values wasn't measured
        (could destroy whole measurement)
        """
        commands = [Command("get-pwm-settings"),
                    Command("get-actinic-continual-settings", [0]),
                    Command("get-actinic-continual-settings", [1]),
                    Command("measure-od", [0, 30]),
                    Command("measure-od", [0, 30]),
                    Command("get-ph", [5, 0]),
                    Command("get-current-temperature"),
                    Command("get-pump-info", [5]),
                    Command("get-o2/h2", [5, 0, self._scheme_manager.to_scheme_bool(True)]),
                    Command("get-co2", [5, self._scheme_manager.to_scheme_bool(True)]),
                    Command("measure-ft", [channel])]

        values = self._scheme_manager.execute(commands)

        result = dict()
        result["pwm_setting"] = self._parser.parse_pwm_settings(values[0])
        result["light_0"] = self._parser.parse_light_intensity(values[1])
        result["light_1"] = self._parser.parse_light_intensity(values[2])
        result["od_0"] = self._parser.parse_od(values[3])
        result["od_1"] = self._parser.parse_od(values[4])
        result["ph"] = self._parser.parse_ph(values[5])
        result["temp"] = self._parser.parse_temp(values[6])
        result["pump"] = self._parser.parse_pump_params(values[7])
        result["o2"] = self._parser.parse_o2(values[8])
        result["co2"] = self._parser.parse_co2(values[9])
        result["ft"] = self._parser.parse_ft(values[10])

        return result

    def measure_AUX(self, channel):
        """
        Values of AUX auxiliary input voltage.

        :param channel: ???
        :return: ???
        """
        raise NotImplementedError("The method not implemented")

    def flash_LED(self):
        """
        Triggers a flashing sequence and is used to physically identify the PBR.

        :return: True if was successful, False otherwise
        """
        raise NotImplementedError("The method not implemented")

    def get_hardware_address(self):
        """
        Get the MAC address of the PBR.

        :return: the MAC address
        """
        raise NotImplementedError("The method not implemented")

    def get_cluster_name(self):
        """
        The name of the bioreactor array / cluster.

        :return: the cluster name
        """
        raise NotImplementedError("The method not implemented")

    def test_connection(self) -> bool:
        try:
            self.get_temp()
            return True
        except Exception:
            return False

    def disconnect(self) -> None:
        pass
