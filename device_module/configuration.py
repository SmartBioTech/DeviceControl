from typing import Dict


class DeviceConfig:

    def __init__(self, data: Dict):
        self.__dict__.update(data)