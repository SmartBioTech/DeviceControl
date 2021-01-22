from core.device.abstract import Connector
from custom.devices.SEDtronic.libs.Connection import Connection


class U1W_TVSL(Connector):
    def __init__(self, config: dict):
        super(U1W_TVSL, self).__init__(config)
        self.connection = Connection(self.address, "8080", self.device_id)
        self.interpreter = {
            "1": self.get_temperature,
            "2": self.get_humidity,
            "3": self.get_illuminance,
            "4": self.measure_all
        }

    def get_temperature(self, temp_unit="C"):
        """
        Get sensor temperature in specified units (default is degrees of Celsius).
        :param unit: Temperature unit ("C" for Celsius, "F" for Farenheit)
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

    def get_illuminance(self):
        """
        Get sensor illuminance (illuminance in lux).
        :return: Current illuminance value.
        """
        sensor, codes = self.connection.read_sensor()
        if sensor.status_code != codes.ok:
            raise Exception(sensor.status_code)

        return {'vis': float(sensor.json()['vis'])}

    def measure_all(self, temp_unit="C"):
        """
        Get sensor temperature in specified units (default is degrees of Celsius), humidity in % and illuminance in lux.
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
            "temperature": temp,
            "humidity": float(sensor.json()['humidity']),
            "illuminance": float(sensor.json()['vis'])
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
