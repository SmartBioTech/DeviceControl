from custom.devices.PSI.java.abstract.java_device import JavaDevice


class GAS(JavaDevice):
    def __init__(self, config: dict):
        super(GAS, self).__init__(config, "custom/devices/PSI/java/lib/config/device_GAS.config")
        self.interpreter = {
            "1": self.get_flow,
            "2": self.get_flow_target,
            "3": self.set_flow_target,
            "4": self.get_flow_max,
            "5": self.get_pressure,
            "6": self.measure_all,
            "7": self.get_co2_air,
            "8": self.get_small_valves,
            "9": self.set_small_valves,
        }

    def get_co2_air(self):
        """
        Measures CO2 in air.
        :return: measured CO2 in air
        """
        msg = self.device.send("get-co2-air")
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getParam(0)

    def get_small_valves(self):
        """
        Obtain settings of individual vents of GAS device.
        Represented as one byte, where first 6 bits represent
        vents indexed as in a picture scheme available here:
        https://i.imgur.com/jSeFFaO.jpg
        :return: byte representation of vents settings.
        """

        msg = self.device.send("get-small-valves")
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getParam(0)

    def set_small_valves(self, mode):
        """
        Changes settings of individual vents of GAS device.
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
        msg = self.device.send("set-small-valves", mode)
        return not msg.isError()

    def get_flow(self, repeats):
        """
        Actual flow being send from GAS to the PBR.
        :param repeats: the number of measurement repeats
        :return: The current flow in L/min.
        """
        msg = self.device.send("get-flow", repeats)
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)

    def get_flow_target(self):
        """
        Actual desired flow.
        :return: The desired flow in L/min.
        """
        msg = self.device.send("get-flow-target")
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)

    def set_flow_target(self, flow):
        """
        Set flow we want to achieve.
        :param flow: flow in L/min we want to achieve (max given by get_flow_max)
        :return: True if was successful, False otherwise.
        """
        msg = self.device.send("set-flow-target", flow)
        return not msg.isError()

    def get_flow_max(self):
        """
        Maximal allowed flow.
        :return: The maximal flow in L/min
        """
        msg = self.device.send("get-flow-max")
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)

    def get_pressure(self, repeats=5, wait=0):
        """
        Current pressure.
        :param repeats: the number of measurement repeats
        :param wait: waiting time between individual repeats
        :return: Current pressure in ???
        """
        msg = self.device.send("get-pressure", repeats, wait)
        if msg.isError():
            raise Exception(msg.getError())

        return msg.getDoubleParam(0)


    def measure_all(self):
        """
        Measures all basic measurable values.
        """
        measure_all_dict = dict()

        try:
            measure_all_dict["co2_air"] = True, self.get_co2_air()
        except Exception:
            measure_all_dict["co2_air"] = False, "cannot measure co2 air"

        try:
            measure_all_dict["flow"] = True, self.get_flow(5)
        except Exception:
            measure_all_dict["flow"] = False, "cannot get flow"

        # try:
        #     measure_all_dict["pressure"] = True, self.get_pressure(5, 0)
        # except Exception:
        #     measure_all_dict["pressure"] = False, "cannot get pressure"

        return measure_all_dict

    def test_connection(self) -> bool:
        try:
            self.get_co2_air()
            return True
        except Exception:
            return False
