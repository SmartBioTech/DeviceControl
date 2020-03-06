from math import log10


def from_scheme_bool(value):
    return True if value == "#t" else False


class Parser:
    """
    PBR
    """

    @staticmethod
    def parse_temp_settings(results, value):
        values = value[0].rstrip()[1:-1].split()
        return dict(zip(results, list(map(float, values[1:-1]))))

    @staticmethod
    def parse_temp(value):
        return float(value[0])

    @staticmethod
    def parse_ph(value):
        return float(value[0])

    @staticmethod
    def parse_od(value):
        result = value[0].rstrip().split()
        return -log10((int(result[1]) - int(result[2][:-1])) / 40000)

    @staticmethod
    def parse_pump_params(value):
        result = value[0].rstrip()[1:-1].split()
        return {"direction": int(result[1]), "on": from_scheme_bool(result[2]),
                "valves": int(result[3]), "flow": float(result[4]),
                "min": float(result[5]), "max": float(result[6])}

    @staticmethod
    def parse_light_intensity(value):
        result = value[0].rstrip()[1:-1].split()
        return {"intensity": float(result[1]), "max": float(result[2]),
                "on": from_scheme_bool(result[3])}

    @staticmethod
    def parse_pwm_settings(value):
        result = value[0].rstrip()[1:-1].split()
        return {"pulse": result[1], "min": result[2],
                "max": result[3], "on": from_scheme_bool(result[4])}

    @staticmethod
    def parse_o2(value):
        return float(value[0].rstrip())

    @staticmethod
    def parse_thermoregulator_settings(value):
        result = value[0].rstrip()[1:-1].split()
        return {"temp": float(result[1]), "min": float(result[2]),
                "max": float(result[3]), "on": int(result[4])}

    @staticmethod
    def parse_ft(value):
        return float(value[0].rstrip())

    @staticmethod
    def parse_co2(value):
        return float(value[0].rstrip())

    """
    GAS
    """

    @staticmethod
    def parse_co2_air(value):
        return float(value[0].rstrip())

    @staticmethod
    def parse_small_valves(value):
        return bin(int(value[0].rstrip()))[2:]

    @staticmethod
    def parse_flow(value):
        return float(value[0].rstrip())

    @staticmethod
    def parse_flow_target(value):
        return float(value[0].rstrip())

    @staticmethod
    def parse_flow_max(value):
        return float(value[0].rstrip())

    @staticmethod
    def parse_pressure(value):
        return float(value[0].rstrip())
