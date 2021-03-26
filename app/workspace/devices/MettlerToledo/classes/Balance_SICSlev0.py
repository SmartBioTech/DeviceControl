from .. import Connector
from ..libs.commMTSICS_level0 import Connection


class Balance_SICSlev0(Connector):
    def __init__(self, config: dict):
        super(Balance_SICSlev0, self).__init__(config)
        self.connection = Connection(self.address, self.device_id)
        self.interpreter = {
            '1': self.get_weight,
            '2': self.get_info
        }

    def get_weight(self):
        """
        Get actual measured weight.

        WARNING: can raise Exception("Unknown unit %s")

        :return: Current weight in grams and stability of measured weight (1 - stable, 0 - dynamic).
        """
        units = {'kg': 1000, 'lb': 453.5924, 'g': 1, 'oz': 28.34952, 't': 1000000}
        result = self.connection.get_weight()

        try:
            return {'weight': result['value'] * units[result['unit']], 'attribute': int(result['stable'])}
        except KeyError:
            raise Exception("Unknown unit {}".format(result['unit']))

    def get_info(self):
        """
        Get the balance available info.

        :return: Model, SN, SW, capacity and unit.
        """
        result = self.connection.get_info()

        try:
            return result
        except KeyError:
            raise Exception("Balance info error")

    def disconnect(self):
        self.connection.close()
        return True

    def test_connection(self) -> bool:
        try:
            self.connection.get_address()
            return True
        except Exception:
            return False
