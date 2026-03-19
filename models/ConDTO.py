from dataclasses import dataclass

@dataclass
class ConDto:
    """DTO para hoja CON"""
    co_cue: str
    SaldoInicial: float
    MontoD: float
    MontoH: float
    EsActivo: str
    EsPasivo: str
    EsCapital: str
    EsIngEgr: str
    EsAdicional: str
    detalle: str
    des_cue: str
    co_cuepadre: str
    NivelCuenta: str
    comp_num: str
    fec_emis: str
    descri: str
    reng_num: str
    docref: str
    IncluirAsiento: str
    SinCuentaMadre: str
    debe_new: float
    haber_new: float
    coincidence: int = 0  # Campo adicional para marcar coincidencias