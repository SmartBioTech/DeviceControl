from device_module.device_connector.PSI_test import GAS as testGAS, GMS as testGMS, PBR as testPBR
from device_module.device_connector.PSI_scheme import GAS as schemeGAS, GMS as schemeGMS, PBR as schemePBR
from device_module.device_connector.PSI_java import GMS as javaGMS, PBR as javaPBR, GAS as javaGAS
from device_module.device_connector.Phenometrics import PBR as phPBR
from device_module.device_connector.abstract.device import Device

classes = {
    "test": {
        "PBR": testPBR.PBR,
        "GAS": testGAS.GAS,
        "GMS": testGMS.GMS,
    },

    "PSI_scheme": {
        "PBR": schemePBR.PBR,
        "GAS": schemeGAS.GAS,
        "GMS": schemeGMS.GMS,
    },

    "PSI_java": {
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
