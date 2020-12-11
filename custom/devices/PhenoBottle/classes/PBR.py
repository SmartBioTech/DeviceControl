from core.device.abstract import Connector
from custom.devices.PhenoBottle.libs.communication import Connection

import math


class PBR(Connector):
    def __init__(self, config):
        super(PBR, self).__init__(config)
        self.connection = Connection(self.address, self.port)
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
        raise NotImplementedError("The method not implemented")

    def get_temp(self):
        """
        Get current temperature in Celsius degree.

        :return: The current temperature.
        """
        result = self.connection.execute_command(b'MeasureTemperature')
        data = [float(s) for s in result.split(",")]
        return {'temp': data[0]}

    def set_temp(self, temp):
        """
        Set desired temperature in Celsius degree.

        :param temp: The temperature.
        :return: True if was successful, False otherwise.
        """
        raise NotImplementedError("The method not implemented")

    def get_ph(self):
        """
        Get current pH (dimensionless.)

        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: The current pH.
        """
        raise NotImplementedError("The method not implemented")

    def measure_od(self, channel=0, initial_optical_density=800):
        """
        Measure current Optical Density (OD, dimensionless).

        :param channel: unused
        :param initial_optical_density: TBA
        :return: Measured OD
        """
        result = self.connection.execute_command(b'MeasureOpticalDensity')
        data = [float(s) for s in result.split(",")]
        initial_transmittance = data[0] / initial_optical_density
        calc_optical_density = (-math.log10(initial_transmittance))
        return {'od': calc_optical_density, 'channel': channel}

    def get_pump_params(self, pump):
        """
        Get parameters for given pump.

        :param pump: Given pump
        :return: The current settings structured in a dictionary.
        """
        raise NotImplementedError("The method not implemented")

    def set_pump_params(self, flow, pump=0, direction=0):
        """
        Set speed of peristaltic motor.

        :param pump: unused
        :param direction: unused
        :param flow: Desired speed
        """
        return {'success': self.connection.motor_speed(self.connection.peristaltic_motor, flow)}

    def set_pump_state(self, on, direction, pump=0):
        """
        Turns on/off given pump.

        :param pump: unused
        :param on: True to turn on, False to turn off
        :return: True if was successful, False otherwise.
        """
        if on:
            return {'success': self.connection.motor_direction(self.connection.peristaltic_motor, True)}
        else:
            return {'success': self.connection.motor_stop(self.connection.peristaltic_motor)}

    def get_light_intensity(self, channel=0):
        """
        Checks for current light intensity.

        :param channel: unused
        :return: current light intensity (float) in μE,
        """
        return {'light_intensit': self.connection.execute_command(b'MeasureLightIntensity')}

    def set_light_intensity(self, intensity, channel=0):
        """
        Control LED panel on photobioreactor.

        :param channel: unused
        :param intensity: Desired intensity
        """
        return {"success": self.connection.motor_speed(self.connection.light_control, intensity)}

    def turn_on_light(self, on, channel=0):
        """
        Turn on/off LED panel on photobioreactor.

        :param channel: unused
        :param on: True turns on, False turns off
        """
        if on:
            return {'success': self.connection.motor_direction(self.connection.light_control, False)}
        else:
            return {'success': self.connection.motor_stop(self.connection.light_control)}

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

        :param value: desired mixing speed
        :param on: True turns on, False turns off
        """
        if on:
            self.connection.motor_direction(self.connection.mixing_motor, False)
            self.connection.motor_speed(self.connection.mixing_motor, value)
        else:
            self.connection.motor_stop(self.connection.mixing_motor)
        return {'success': True}

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
        raise NotImplementedError("The method not implemented")

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
        raise NotImplementedError("The method not implemented")

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
