from dataclasses import dataclass

@dataclass
class AdmDto:
    """DTO para hoja ADM"""
    nro_doc: str
    co_tipo_doc: str
    co_ven: str
    co_cli: str
    fec_emis: str
    fec_venc: str
    anulado: str
    tasa: float
    total_neto: float
    saldo: float
    co_mone_doc: str
    tasa_doc: float
    Rel_Inv: str
    cli_des: str
    observa: str
    tipo_mov: str
    Mon_Rep: float
    Mon_Fil: float
    total_neto_new: float
    saldo_new: float

    # Aditional fields for processing (not from Excel)
    has_coincidence: bool = False
    row_coincidence: int = None
    text_coincidence: str = None