from .. import Command, BaseTask, Observable, Observer
from . import PBR, GAS, GMS, TH_IB2, U1W_TVSL, SICS, general

classes = {
    "PSI": {
        "PBR_measure_all": PBR.PBRMeasureAll,
        "GAS_measure_all": GAS.GASMeasureAll,
        "GMS_measure_all": GMS.GMSMeasureAll
    },

    "MettlerToledo": {
        "Balance_measure_weight": SICS.MeasureWeight
    },

    "SEDtronic": {
        "U1W_TVSL_measure_all": U1W_TVSL.MeasureAll,
        "TH_IB2_measure_all": TH_IB2.MeasureAll,
    },

    "General": {
        "PBR_general_pump": PBR.PBRGeneralPump,
        "measure_all_desync": general.MeasureAllDesync,
        "periodic_regime": general.PeriodicRegime
    }
}
