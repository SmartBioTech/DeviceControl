from custom.devices import MettlerToledo
from custom.devices import Phenometrics
from custom.devices import SEDtronic
from custom.devices.PSI import java, test

classes = {
    "PSI": {
        "PBR": java.PBR,
        "GAS": java.GAS,
        "GMS": java.GMS
    },

    "test": {
        "PBR": test.PBR,
        "GAS": test.GAS,
        "GMS": test.GMS
    },

    "Phenometrics": {
        "PBR": Phenometrics.PBR
    },

    "SEDtronic": {
        "U1WTVSL": SEDtronic.U1W_TVSL,
        "1WTHIB2": SEDtronic.TH_IB2
    },

    "MettlerToledo": {
        "SICS": MettlerToledo.SICS
    }
}
