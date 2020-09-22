from custom.tasks import PBR, GAS, GMS, TH_IB2, U1W_TVSL, SICS

classes = {
    "Balance_measure_weight": SICS.MeasureWeight,
    "U1W_TVSL_measure_all": U1W_TVSL.MeasureAll,
    "TH_IB2_measure_all": TH_IB2.MeasureAll,
    "PBR_measure_all": PBR.PBRMeasureAll,
    "PSI_PBR_pump": PBR.PBRGeneralPump,
    "GAS_measure_all": GAS.GASMeasureAll,
    "GMS_measure_all": GMS.GMSMeasureAll,
    "PBR_day_night_regime": PBR.PBRDayNightRegime
}
