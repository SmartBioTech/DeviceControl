from custom.devices.PSI import java, test
from custom.devices import Phenometrics
from custom.devices import SEDtronic
from custom.devices import MettlerToledo


classes = {
    "MettlerToledo_SICS": MettlerToledo.SICS,
    "UniPi_1WTHIB2" : SEDtronic.TH_IB2,
    "SEDtronic_U1WTVSL" : SEDtronic.U1W_TVSL,
    "Phenometrics_PBR": Phenometrics.PBR,
    "PSI_java_PBR": java.PBR,
    "PSI_java_GAS": java.GAS,
    "PSI_java_GMS": java.GMS,
    "test_PBR": test.PBR,
    "test_GAS": test.GAS,
    "test_GMS": test.GMS
}
