from device_connector.Phenometrics.libs.communication import Connection
from device_connector.abstract.device import Device

from device_module.configuration import DeviceConfig


class PBR(Device):
    def __init__(self, config: DeviceConfig):
        super(PBR, self).__init__(config)
        self.connection = Connection(config.host_address,
                                     config.host_port,
                                     config.encryption_key)

        self.id = config.device_id
        self.address = config.host_address

    def get_temp_settings(self):
        """
        Get information about currently set temperature, maximal and
        minimal allowed temperature.

        :return: The current settings structured in a dictionary.
        """
        raise NotImplementedError("The method not implemented")

    def get_temp(self):
        """
        Get current temperature in Celsius degree.

        :return: The current temperature.
        """
        success, result = self.connection.send_command(self.ID, 'measureTemperature', [])
        if not success:
            raise Exception(result)
        return float(result)

    def set_temp(self, temp):
        """
        Set desired temperature in Celsius degree.

        :param temp: The temperature.
        :return: True if was successful, False otherwise.
        """
        success, result = self.connection.send_command(self.ID, 'setTemperature', [temp])
        if not success:
            raise Exception(result)
        return float(result) == temp

    def get_ph(self):
        """
        Get current pH (dimensionless.)

        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: The current pH.
        """
        success, result = self.connection.send_command(self.ID, 'measurePH', [])
        if not success:
            raise Exception(result)
        return float(result)

    def measure_od(self, channel=0):
        """
        Measure current Optical Density (OD, dimensionless).

        :param channel: which channel should be measured
        :return: Measured OD
        """
        variant = ["measureOD1", "measureOD2"]
        success, result = self.connection.send_command(self.ID, variant[channel], [])
        if not success:
            raise Exception(result)
        return float(result)

    def get_pump_params(self, pump):
        """
        Get parameters for given pump.

        :param pump: Given pump
        :return: The current settings structured in a dictionary.
        """
        raise NotImplementedError("The method not implemented")

    def set_pump_params(self, pump, direction, flow):
        """
        Set up the rotation direction and flow for given pump.

        :param pump: Given pump
        :param direction: Rotation direction (1 right, -1 left)
        :param flow: Desired flow rate
        :return:  True if was successful, False otherwise.
        """
        raise NotImplementedError("The method not implemented")

    def set_pump_state(self, pump, on):
        """
        Turns on/off given pump.

        :param pump: ID of a pump
        :param on: True to turn on, False to turn off
        :return: True if was successful, False otherwise.
        """
        success, result = self.connection.send_command(self.ID, 'setAux2', [int(on)])
        if not success:
            raise Exception(result)
        return int(result) == int(on)

    def get_light_intensity(self, channel):
        """
        Checks for current (max?) light intensity.

        Items: "intensity": current light intensity (float) in μE,
               "max": maximal intensity (float) in μE,
               "on": True if light is turned on (bool)

        :param channel: Given channel ID
        :return: The current settings structured in a dictionary.
        """
        raise NotImplementedError("The method not implemented")

    def set_light_intensity(self, channel, intensity):
        """
        Control LED panel on photobioreactor.

        :param channel: Given channel (0 for red light, 1 for blue light)
        :param intensity: Desired intensity
        :return: True if was successful, False otherwise.
        """
        success, result = self.connection.send_command(self.ID, 'setSolarLED', [intensity])
        if not success:
            raise Exception(result)
        return float(result) == float(intensity)

    def turn_on_light(self, channel, on):
        """
        Turn on/off LED panel on photobioreactor.

        :param channel: Given channel
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        raise NotImplementedError("The method not implemented")

    def get_pwm_settings(self):
        """
        Checks for current stirring settings.

        Items: "pulse": current stirring in %,
               "min": minimal stirring in %,
               "max": maximal stirring in %,
               "on": True if stirring is turned on (bool)

        :return: The current settings structured in a dictionary.
        """
        raise NotImplementedError("The method not implemented")

    def set_pwm(self, value, on):
        """
        Set stirring settings.
        Channel: 0 red and 1 blue according to PBR configuration.

        :param value: desired stirring pulse
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        success, result = self.connection.send_command(self.ID, 'setStir', [value])
        if not success:
            raise Exception(result)
        return float(result) == float(value)

    def get_o2(self, raw=True, repeats=5, wait=0):
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
        raise NotImplementedError("The method not implemented")

    def get_thermoregulator_settings(self):
        """
        Get current settings of thermoregulator.

        Items: "temp": current temperature in Celsius degrees,
               "min": minimal allowed temperature,
               "max": maximal allowed temperature,
               "on": state of thermoregulator (1 -> on, 0 -> freeze, -1 -> off)

        :return: The current settings structured in a dictionary.
        """
        raise NotImplementedError("The method not implemented")

    def set_thermoregulator_state(self, on):
        """
        Set state of thermoregulator.

        :param on: 1 -> on, 0 -> freeze, -1 -> off
        :return: True if was successful, False otherwise.
        """
        success, result = self.connection.send_command(self.ID, 'stopTemperatureControl', [])
        if not success:
            raise Exception(result)
        return result == "stopTemperatureControl"

    def measure_ft(self, channel):
        """
        ???

        :param channel: ???
        :return: ???
        """
        raise NotImplementedError("The method not implemented")

    def get_co2(self, raw, repeats):
        """
        TBA

        :param raw: True for raw data, False for data ???
        :param repeats: the number of measurement repeats
        :return:
        """
        raise NotImplementedError("The method not implemented")

    def measure_all(self, ft_channel=5, pump_id=5):
        """
        Measures all basic measurable values.

        :param ft_channel: channel for ft_measure
        :param pump_id: id of particular pump
        :return: dictionary of all measured values
        """
        measure_all_dictionary = dict()
        measure_all_dictionary["pwm_settings"] = False, "pwm settings not available for this device_module"
        measure_all_dictionary["light_0"] = False, "light_0 not available for this device_module"
        measure_all_dictionary["light_1"] = False, "light_1 not available for this device_module"

        try:
            measure_all_dictionary["od_0"] = True, self.measure_od(0)
        except Exception:
            measure_all_dictionary["od_0"] = False, "Cannot get od_0"

        try:
            measure_all_dictionary["od_1"] = True, self.measure_od(1)
        except Exception:
            measure_all_dictionary["od_1"] = False, "Cannot get od_1"

        try:
            measure_all_dictionary["ph"] = True, self.get_ph(),
        except Exception:
            measure_all_dictionary["ph"] = False, "Cannot get ph"

        try:
            measure_all_dictionary["temp"] = True, self.get_temp(),
        except Exception:
            measure_all_dictionary["temp"] = False, "Cannot get temp"

        measure_all_dictionary["pump"] = False, "pump settings not available for this device_module"
        measure_all_dictionary["o2"] = False, "o2 settings not available for this device_module"
        measure_all_dictionary["co2"] = False, "co2 settings not available for this device_module"
        measure_all_dictionary["ft"] = False, "ft settings not available for this device_module"

        return measure_all_dictionary

    def measure_AUX(self, channel):
        """
        Values of AUX auxiliary input voltage.

        :param channel: ???
        :return: ???
        """
        variant = ["measureAux1", "measureAux2"]
        success, result = self.connection.send_command(self.ID, variant[channel], [])
        if not success:
            raise Exception(result)
        return float(result)

    def flash_LED(self):
        """
        Triggers a flashing sequence and is used to physically identify the PBR.

        !!! random blank spaces complicate things. Is it like that also with "real" PBR?

        :return: True if was successful, False otherwise
        """
        success, result = self.connection.send_command(self.ID, "flashLED", [])
        if not success:
            raise Exception(result)
        return result.lstrip() == "flashLED"

    def get_hardware_address(self):
        """
        Get the MAC address of the PBR.

        :return: the MAC address
        """
        success, result = self.connection.send_command(self.ID, "getHardwareAddress", [])
        if not success:
            raise Exception(result)
        return result.lstrip()

    def get_cluster_name(self):
        """
        The name of the bioreactor array / cluster.

        :return: the cluster name
        """
        success, result = self.connection.send_command(self.ID, "getMatrixName", [])
        if not success:
            raise Exception(result)
        return result.lstrip()

    def test_connection(self) -> bool:
        try:
            self.get_cluster_name()
            return True
        except Exception:
            return False

    def disconnect(self):
        pass
