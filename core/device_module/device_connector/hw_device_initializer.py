from custom.devices.PSI.test.classes import PBR as testPBR
from custom.devices.PSI.test.classes import GAS as testGAS, GMS as testGMS
from custom.devices.PSI.scheme.classes import PBR as schemePBR, GAS as schemeGAS, GMS as schemeGMS
from custom.devices.PSI.java import GMS as javaGMS, PBR as javaPBR
from custom.devices.PSI.java import GAS as javaGAS
from custom.devices.Phenometrics import PBR as phPBR
from core.device_module.device_connector.abstract.device import Device

classes = {
    "test": {
        "PBR": testPBR.PBR,
        "GAS": testGAS.GAS,
        "GMS": testGMS.GMS,
    },

    "scheme": {
        "PBR": schemePBR.PBR,
        "GAS": schemeGAS.GAS,
        "GMS": schemeGMS.GMS,
    },

    "java": {
        "PBR": javaPBR.PBR,
        "GAS": javaGAS.GAS,
        "GMS": javaGMS.GMS,
    },

    "Phenometrics": {
        "PBR": phPBR.PBR
    }
}


def get_device_type_from_class(class_name: str, device_type: str) -> Device.__class__:
    result = None
    try:
        result = classes.get(class_name).get(device_type)
    finally:
        if result is None:
            raise ModuleNotFoundError("Invalid device_module class or type")
        return result
