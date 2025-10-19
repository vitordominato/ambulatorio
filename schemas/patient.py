# schemas/patient.py
from dataclasses import dataclass

@dataclass
class Patient:
    id: str
    sex: str            # "M" ou "F"
    age: int
    is_health_worker: bool = False

    # HPP
    imc_ge_25: bool = False
    smoker_or_ex: bool = False
    is_pregnant: bool = False
    dm: bool = False
    dpoc: bool = False
    imunossuprimido: bool = False
    cardiovascular_cronica: bool = False
    renal_cronica: bool = False
    hepatica_cronica: bool = False
    neoplasia_ativa: bool = False
    hipertensao_resistente: bool = False
    dm_hba1c_maior_75: bool = False
    alcoolismo: bool = False
    enxaqueca_refrataria: bool = False
    ldl_maior_190: bool = False
    doencas_colageno: bool = False
    uso_aco: bool = False
    transplantado: bool = False

    # HF
    famhx_mama: bool = False
    famhx_prostata: bool = False
    famhx_colorretal: bool = False
    famhx_coronariana: bool = False
    famhx_avc_isquemico: bool = False
    famhx_aaa: bool = False
    famhx_ateromatose: bool = False
    famhx_an_intracraniano: bool = False
    famhx_outro_aneurisma: bool = False

    # Livre
    free_text: str = ""

