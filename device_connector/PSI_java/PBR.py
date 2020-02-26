from device_connector.PSI_java.java_device import JavaDevice
from math import log10


class PBR(JavaDevice):
    def __init__(self, device_id, address):
        super(PBR, self).__init__(device_id, address, "device_connector/PSI_java/lib/config/device_PBR.config")
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

    def get_temp_settings(self):
        """
        Get information about currently set temperature, maximal and
        minimal allowed temperature.
        :return: The current settings structured in a dictionary.
        """

        msg = self.device.send("get-tr-settings")
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "temp_set": msg.getDoubleParam(0),
            "temp_min": msg.getDoubleParam(1),
            "temp_max": msg.getDoubleParam(2),
            "state": msg.getBoolParam(3)
        }

    def get_temp(self):
        """
        Get current temperature in Celsius degree.
        :return: The current temperature.
        """
        msg = self.device.send("get-tr-temp")
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)

    def set_temp(self, temp):
        """
        Set desired temperature in Celsius degree.
        :param temp: The temperature.
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-tr-temp", temp)
        return not msg.isError()

    def get_ph(self, repeats, wait):
        """
        Get current pH (dimensionless.)
        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: The current pH.
        """
        msg = self.device.send("get-ph", repeats, wait)
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)

    def measure_od(self, channel=0, repeats=1):
        """
        Measure current Optical Density (OD, dimensionless).
        :param channel: which channel should be measured
        :param repeats: the number of measurement repeats
        :return: Measured OD
        """
        msg = self.device.send("measure-od", channel, repeats)
        if msg.isError():
            raise Exception(msg.getError())

        # get photon intensity for measuring light and background light
        pi = msg.getDoubleParam(0), msg.getDoubleParam(1)

        # check for dense cultures
        # TODO develop better handling of dense cultures detection. Combine treshold and background readouts.
        if int(pi[0]) > 100:
            od = -log10((int(pi[0]) - int(pi[1])) / 40000)
        else:
            od = 3.0

        return od

    def get_pump_params(self, pump):
        """
        Get parameters for given pump.
        :param pump: Given pump
        :return: The current settings structured in a dictionary.
        """
        msg = self.device.send("get-pump-info", pump)
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "pump_direction": msg.getIntParam(0),
            "pump_on": msg.getBoolParam(1),
            "pump_valves": msg.getIntParam(2),
            "pump_flow": msg.getDoubleParam(3),
            "pump_min": msg.getDoubleParam(4),
            "pump_max": msg.getDoubleParam(5)
        }

    def set_pump_params(self, pump, direction, flow):
        """
        Set up the rotation direction and flow for given pump.
        :param pump: Given pump
        :param direction: Rotation direction (1 right, -1 left)
        :param flow: Desired flow rate
        :return:  True if was successful, False otherwise.
        """
        msg = self.device.send("set-pump-params", pump, direction, flow)
        return not msg.isError()

    def set_pump_state(self, pump, on):
        """
        Turns on/off given pump.
        :param pump: ID of a pump
        :param on: True to turn on, False to turn off
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-pump-state", pump, on)
        return not msg.isError()

    def get_light_intensity(self, channel):
        """
        Checks for current (max?) light intensity.
        Items: "intensity": current light intensity (float) in μE,
               "max": maximal intensity (float) in μE,
               "on": True if light is turned on (bool)
        :param channel: Given channel ID
        :return: The current settings structured in a dictionary.
        """
        msg = self.device.send("get-actinic-light-settings", channel)
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "light_intensity": msg.getDoubleParam(0),
            "light_max": msg.getDoubleParam(1),
            "light_on": msg.getBoolParam(2)
        }

    def set_light_intensity(self, channel, intensity):
        """
        Control LED panel on photobioreactor.
        :param channel: Given channel (0 for red light, 1 for blue light)
        :param intensity: Desired intensity
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-actinic-light-intensity", channel, intensity)
        return not msg.isError()

    def turn_on_light(self, channel, on):
        """
        Turn on/off LED panel on photobioreactor.
        :param channel: Given channel
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-ext-light-state", channel, on)
        return not msg.isError()

    def get_pwm_settings(self):
        """
        Checks for current stirring settings.
        Items: "pulse": current stirring in %,
               "min": minimal stirring in %,
               "max": maximal stirring in %,
               "on": True if stirring is turned on (bool)
        :return: The current settings structured in a dictionary.
        """
        msg = self.device.send("get-pwm-settings")
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "pwm_pulse": msg.getIntParam(0),
            "pwm_min": msg.getIntParam(1),
            "pwm_max": msg.getIntParam(2),
            "pwm_on": msg.getParam(3),
        }

    def set_pwm(self, value, on):
        """
        Set stirring settings.
        Channel: 0 red and 1 blue according to PBR configuration.
        :param value: desired stirring pulse
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-pwm", value, on)
        return not msg.isError()

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

        msg = self.device.send("get-o2/h2", repeats, wait, raw)
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)

    def get_thermoregulator_settings(self):
        """
        Get current settings of thermoregulator.
        Items: "temp": current temperature in Celsius degrees,
               "min": minimal allowed temperature,
               "max": maximal allowed temperature,
               "on": state of thermoregulator (1 -> on, 0 -> freeze, -1 -> off)
        :return: The current settings structured in a dictionary.
        """
        msg = self.device.send("get-tr-settings")
        return {
            "temp": msg.getDoubleParam(0),
            "temp_min": msg.getDoubleParam(1),
            "temp_max": msg.getDoubleParam(2),
            "temp_on": msg.getIntParam(3),
        }

    def set_thermoregulator_state(self, on):
        """
        Set state of thermoregulator.
        :param on: 1 -> on, 0 -> freeze, -1 -> off
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-tr-state", on)
        return not msg.isError()

    def measure_ft(self, channel):
        """
        ???
        :param channel: ???
        :return: ???
        """
        msg = self.device.send("measure-ft", channel)
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "flash": msg.getIntParam(0),
            "background": msg.getIntParam(1)
        }

    def measure_qy(self, channel):
        """ Measure steady-state terminal and maximal fluorescence and calculate quantum yield

        !This measure NOT to be included with measure_all
        
        Arguments:
            channel {int} -- measuring light channel

        Returns:
            qy {real} -- quantum yield calculated as (fm-ft)/fm
            ft-flash {int} -- steady-state terminal fluorescence
            ft-background {int} -- steady-state terminal fluorescence background signal
            fm-flash{int} -- maximal fluorescence
            fm-background {int} -- maximal fluorescence background signal
            sp-delay-cycles {int} -- ?number of cycles before reaching stable signal?
        """
        msg = self.device.send("measure-qy", channel)
        if msg.isError():
            raise Exception(msg.getError())

        return {
            # TODO: implement check for extreme / noisy measures that could possibly lead to crazy results in qy calculations
            "qy": ((msg.getIntParam(2) - msg.getIntParam(3)) - (msg.getIntParam(0) - msg.getIntParam(1))) / (
                        msg.getIntParam(2) - msg.getIntParam(3)),
            "flash-ft": msg.getIntParam(0),
            "background-ft": msg.getIntParam(1),
            "flash-fm": msg.getIntParam(2),
            "background-fm": msg.getIntParam(3),
            "delay-cycles": msg.getIntParam(4)
        }

    def get_co2(self, raw=True, repeats=5):
        """
        TBA
        :param raw: True for raw data, False for data ???
        :param repeats: the number of measurement repeats
        :return:
        """
        msg = self.device.send("get-co2", repeats, raw)
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)

    def measure_all(self, ft_channel=5, pump_id=5):
        """
        Measures all basic measurable values.

        :param ft_channel: channel for ft_measure
        :param pump_id: id of particular pump
        :return: dictionary of all measured values
        """
        measure_all_dictionary = dict()
        try:
            measure_all_dictionary["pwm_settings"] = True, self.get_pwm_settings()
        except Exception:
            measure_all_dictionary["pwm_settings"] = False, "Cannot get pwm settings"

        try:
            measure_all_dictionary["light_0"] = True, self.get_light_intensity(0)
        except Exception:
            measure_all_dictionary["light_0"] = False, "Cannot get light_0"

        try:
            measure_all_dictionary["light_1"] = True, self.get_light_intensity(1)
        except Exception:
            measure_all_dictionary["light_1"] = False, "Cannot get light_1"

        try:
            measure_all_dictionary["od_0"] = True, self.measure_od(0, 30)
        except Exception:
            measure_all_dictionary["od_0"] = False, "Cannot get od_0"

        try:
            measure_all_dictionary["od_1"] = True, self.measure_od(1, 30)
        except Exception:
            measure_all_dictionary["od_1"] = False, "Cannot get od_1"

        try:
            measure_all_dictionary["ph"] = True, self.get_ph(5, 0),
        except Exception:
            measure_all_dictionary["ph"] = False, "Cannot get ph"

        try:
            measure_all_dictionary["temp"] = True, self.get_temp(),
        except Exception:
            measure_all_dictionary["temp"] = False, "Cannot get temp"

        try:
            measure_all_dictionary["pump"] = True, self.get_pump_params(pump_id),
        except Exception:
            measure_all_dictionary["pump"] = False, "Cannot get pump"

        try:
            measure_all_dictionary["o2"] = True, self.get_o2()
        except Exception:
            measure_all_dictionary["o2"] = False, "Cannot get o2"

        try:
            measure_all_dictionary["co2"] = True, self.get_co2()
        except Exception:
            measure_all_dictionary["co2"] = False, "Cannot get co2"

        try:
            measure_all_dictionary["ft"] = True, self.measure_ft(ft_channel)
        except Exception:
            measure_all_dictionary["ft"] = False, "Cannot measure ft"

        return measure_all_dictionary

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
            self.get_pwm_settings()
            return True
        except Exception:
            return False
