from .. import Connector
from ..libs.Connection import Connection


class TH_IB2(Connector):
    """
    On-wall temperature + humidity sensor.

    Commands:

    - "1": self.get_temperature,
    - "2": self.get_humidity,
    - "3": self.measure_all
    """
    def __init__(self, config: dict):
        super(TH_IB2, self).__init__(config)
        self.connection = Connection(self.address, "8080", self.device_id)
        self.interpreter = {
            "1": self.get_temperature,
            "2": self.get_humidity,
            "3": self.measure_all
        }

    def get_temperature(self, temp_unit="C"):
        """
        Get sensor temperature in specified units (default is degrees of Celsius).

        :param temp_unit: Temperature unit ("C" for Celsius, "F" for Farenheit)
        :return: Current temperature value in selected unit.
        """
        sensor, codes = self.connection.read_sensor()
        if sensor.status_code != codes.ok:
            raise Exception(sensor.status_code)

        temp = float(sensor.json()['temp'])

        if temp_unit is "F":
            temp = temp*9/5+32

        return {'temp': temp}

    def get_humidity(self):
        """
        Get sensor humidity (relative humidity in %).

        :return: Current humidity value.
        """
        sensor, codes = self.connection.read_sensor()
        if sensor.status_code != codes.ok:
            raise Exception(sensor.status_code)

        return {'humidity': float(sensor.json()['humidity'])}

    def measure_all(self, temp_unit="C"):
        """
        Get sensor temperature in specified units (default is degrees of Celsius) and humidity in %.

        :param unit: Temperature unit ("C" for Celsius, "F" for Farenheit)
        :return: Current temperature and humidity values in selected unit.
     
        """
        sensor, codes = self.connection.read_sensor()
        if sensor.status_code != codes.ok:
            raise Exception(sensor.status_code)

        temp = float(sensor.json()['temp'])

        if temp_unit is "F":
            temp = temp*9/5+32

        return True, {
            "temp": temp,
            "humidity": float(sensor.json()['humidity'])
        }

    def disconnect(self):
        # not necessary to implement
        return True

    def test_connection(self) -> bool:
        try:
            self.get_temperature()
            return True
        except Exception:
            return False
