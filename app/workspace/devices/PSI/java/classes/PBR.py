from ..abstract.java_device import JavaDevice
from math import log10


class PBR(JavaDevice):
    def __init__(self, config: dict):
        super(PBR, self).__init__(config, "app/workspace/devices/PSI/java/lib/config/device_PBR.config")
        self.interpreter = {
            "1": self.get_temp_settings,
            "2": self.get_temp,
            "3": self.set_temp,
            "4": self.get_ph,
            "5": self.measure_od,
            "6": self.get_pump_params,
            "7": self.set_pump_params,
            "8": self.set_pump_state,
            "9": self.get_light_intensity,
            "10": self.set_light_intensity,
            "11": self.turn_on_light,
            "12": self.get_pwm_settings,
            "13": self.set_pwm,
            "14": self.get_o2,
            "15": self.set_thermoregulator_state,
            "16": self.measure_ft,
            "17": self.get_co2,
            "18": self.measure_all,
            "19": self.measure_AUX,
            "20": self.flash_LED,
            "21": self.get_hardware_address,
            "22": self.get_cluster_name
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
            "temp": msg.getDoubleParam(0),
            "temp_min": msg.getDoubleParam(1),
            "temp_max": msg.getDoubleParam(2),
            "temp_on": int(msg.getBoolParam(3))
        }

    def get_temp(self):
        """
        Get current temperature in Celsius degree.
        :return: The current temperature.
        """
        msg = self.device.send("get-tr-temp")
        if msg.isError():
            raise Exception(msg.getError())

        return {'temp': msg.getDoubleParam(0)}

    def set_temp(self, temp):
        """
        Set desired temperature in Celsius degree.
        :param temp: The temperature.
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-tr-temp", temp)
        return {'success': not msg.isError()}

    def get_ph(self, repeats=5, wait=0):
        """
        Get current pH (dimensionless.)
        :param repeats: The number of measurement repeats
        :param wait: Waiting time between individual repeats
        :return: The current pH.
        """
        msg = self.device.send("get-ph", repeats, wait)
        if msg.isError():
            raise Exception(msg.getError())

        return {'pH': msg.getDoubleParam(0)}

    def measure_od(self, attribute=0, repeats=5):
        """
        Measure current Optical Density (OD, dimensionless).
        :param attribute: Optical path to be measured ()
        :param repeats: The number of measurement repeats
        :return: Measured OD
        """
        msg = self.device.send("measure-od", attribute, repeats)
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

        return {'od': od, 'attribute': attribute}

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
            "pump_on": int(msg.getBoolParam(1)),
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
        return {'success': not msg.isError()}

    def set_pump_state(self, pump, on):
        """
        Turns on/off given pump.
        :param pump: ID of a pump
        :param on: True to turn on, False to turn off
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-pump-state", pump, on)
        return {'success': not msg.isError()}

    def get_light_intensity(self, attribute=0):
        """
        Checks for current (max?) light intensity.
        Items: "intensity": current light intensity (float) in μE,
               "max": maximal intensity (float) in μE,
               "on": True if light is turned on (bool)
        :param attribute: Given attribute ID
        :return: The current settings structured in a dictionary.
        """
        msg = self.device.send("get-actinic-light-settings", attribute)
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "light_intensity": msg.getDoubleParam(0),
            "light_max": msg.getDoubleParam(1),
            "light_on": int(msg.getBoolParam(2)),
            "attribute": attribute
        }

    def set_light_intensity(self, attribute, intensity):
        """
        Control LED panel on photobioreactor.
        :param attribute: Given attribute (0 for red light, 1 for blue light)
        :param intensity: Desired intensity
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-actinic-light-intensity", attribute, intensity)
        return {'success': not msg.isError()}

    def set_ratio_light_intensity(self, intensity, ratio=0.5):
        """
        Set target light intensity as a sum of red and blue lights, mixed according to given ratio.
        :param intensity: target light intensity
        :param ratio: (red/ratio) == (blue/(1-ratio))
        :return: True if both were successful, False otherwise.
        """
        msg1 = self.device.send("set-actinic-light-intensity", 0, intensity * ratio)        # red
        msg2 = self.device.send("set-actinic-light-intensity", 1, intensity * (1 - ratio))  # blue
        return not msg1.isError() and not msg2.isError()

    def turn_on_light(self, attribute=0, on=True):
        """
        Turn on/off photobioreactor LED panel.
        :param attribute: Given attribute
        :param on: True turns on, False turns off
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-actinic-light-state", attribute, on)
        return {'success': not msg.isError()}

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
        For standard stirrer max (100 %) intensity is 600 rpm.

        :param value: desired stirring intensity in %
        :param on: True turns on, False turns off
        :return: True if successful, False otherwise.
        """
        msg = self.device.send("set-pwm", value, on)
        return {'success': not msg.isError()}

    def get_o2(self, raw=True, repeats=5, wait=0):
        """
        Checks for concentration of dissociated O2.

        :param raw: True for raw data, False for data calculated according to temperature calibration
        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: The current settings structured in a dictionary.
        """

        msg = self.device.send("get-o2/h2", repeats, wait, raw)
        if msg.isError():
            raise Exception(msg.getError())

        return {'o2': msg.getDoubleParam(0)}

    def set_thermoregulator_state(self, on=0):
        """
        Set state of thermoregulator.
        :param on: 0 - off, 1 - on, 2 - freeze
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-tr-state", on)
        return {'success': not msg.isError()}

    def measure_ft(self, attribute=0):
        """
        Measure steady-state terminal fluorescence.
        :param attribute: 0 -> blue (455 nm) measuring LEDs, 1 -> red (627 nm) measuring LEDs
        :return: fluorescence value in arbitrary units
        """
        msg = self.device.send("measure-ft", attribute)
        if msg.isError():
            raise Exception(msg.getError())

        return {
            "ft_flash": msg.getIntParam(0),
            "ft_background": msg.getIntParam(1),
            "attribute": attribute
        }

    def measure_qy(self, attribute=0):
        """ Measure steady-state terminal and maximal fluorescence and calculate quantum yield
        !This measure NOT to be included with measure_all

        Arguments:
            attribute {int} -- measuring light attribute
        Returns:
            qy {real} -- quantum yield calculated as (fm-ft)/fm
            ft-flash {int} -- steady-state terminal fluorescence
            ft-background {int} -- steady-state terminal fluorescence background signal
            fm-flash{int} -- maximal fluorescence
            fm-background {int} -- maximal fluorescence background signal
            sp-delay-cycles {int} -- ?number of cycles before reaching stable signal?
        """
        msg = self.device.send("measure-qy", attribute)
        if msg.isError():
            raise Exception(msg.getError())

        return {
            # TODO: implement check for extreme / noisy measures that could possibly lead to crazy results in qy calculations
            "qy": ((msg.getIntParam(2) - msg.getIntParam(3)) - (msg.getIntParam(0) - msg.getIntParam(1))) / (
                    msg.getIntParam(2) - msg.getIntParam(3)),
            "ft-flash": msg.getIntParam(0),
            "ft-background": msg.getIntParam(1),
            "fm-flash": msg.getIntParam(2),
            "fm-background": msg.getIntParam(3),
            "delay-cycles": msg.getIntParam(4),
            "attribute": attribute
        }

    def get_co2(self, raw=True, repeats=5):
        """
        Measure dissolved CO2 concentration.
        :param raw: True for raw data, False for calibrated data
        :param repeats: the number of measurement repeats
        :return: averaged CO2 concentration
        """
        msg = self.device.send("get-co2", repeats, raw)
        if msg.isError():
            raise Exception(msg.getError())

        return {'co2': msg.getDoubleParam(0)}

    def measure_all(self, pump_id=5):
        """
        Measures all basic measurable values.
        :param ft_attribute: attribute for ft_measure
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
            measure_all_dictionary["od_0"] = False, "Cannot get OD_0"

        try:
            measure_all_dictionary["od_1"] = True, self.measure_od(1, 30)
        except Exception:
            measure_all_dictionary["od_1"] = False, "Cannot get OD_1"

        try:
            measure_all_dictionary["ph"] = True, self.get_ph(5, 0),
        except Exception:
            measure_all_dictionary["ph"] = False, "Cannot get pH"

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
            measure_all_dictionary["o2"] = False, "Cannot get O2"

        try:
            measure_all_dictionary["co2"] = True, self.get_co2()
        except Exception:
            measure_all_dictionary["co2"] = False, "Cannot get CO2"

        try:
            measure_all_dictionary["ft_0"] = True, self.measure_ft(0)
        except Exception:
            measure_all_dictionary["ft_0"] = False, "Cannot measure ft_0"

        try:
            measure_all_dictionary["ft_1"] = True, self.measure_ft(1)
        except Exception:
            measure_all_dictionary["ft_1"] = False, "Cannot measure ft_1"

        return measure_all_dictionary

    def measure_AUX(self, attribute):
        """
        Values of AUX auxiliary input voltage.
        :param attribute: ???
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
