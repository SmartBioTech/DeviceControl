from core.device.abstract import Connector
from custom.devices.MettlerToledo.libs.Connection import Connection


class SICS(Connector):
    def __init__(self, config: dict):
        super(SICS, self).__init__(config)
        self.connection = Connection(self.address, self.device_id)
        self.interpreter = {
            '1': self.get_weight,
            '2': self.get_info
        }

    def get_weight(self):
        """
        Get actual measured weight in set units.

        :return: Current weight in grams.
        """
        result = self.connection.get_weight()
        if result['unit'] != "g":
            if result['unit'] == "kg":
                result['value'] *= 1000
            elif result['unit'] == "lb":
                result['value'] *= 453.5924
            elif result['unit'] == "oz":
                result['value'] *= 28.34952
            elif result['unit'] == "t":
                result['value'] *= 1000000
        return {'weight': result['value']}

    def get_info(self):
        """
        Get the balance available info.

        :return: Model, SN, SW, capacity and unit.
        """
        return self.connection.get_info()

    def disconnect(self):
        self.connection.close()
        return True

    def test_connection(self) -> bool:
        try:
            self.connection.get_address()
            return True
        except Exception:
            return False
