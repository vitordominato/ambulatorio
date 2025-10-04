from pydantic import BaseModel
from typing import List, Literal

class Patient(BaseModel):
    id: str
    name: str
    sex: Literal["M","F","I"]
    age: int
    comorbidities: List[str] = []

    # tabagismo em categorias (novo)
    smoking_status: Literal["Não", "Sim", "Ex-tabagista", "Passivo"] = "Não"

    is_health_worker: bool = False

    # fatores/antecedentes (chaves idênticas às do factors.yaml)
    imc_ge_25: bool = False
    smoker_or_ex: bool = False
    is_pregnant: bool = False  # mapeia "gestante"
    famhx_mama: bool = False
    famhx_prostata: bool = False
    famhx_colorretal: bool = False
    dm: bool = False
    dpoc: bool = False
    imunossuprimido: bool = False
    cardiovascular_cronica: bool = False
    renal_cronica: bool = False
    hepatica_cronica: bool = False
    neoplasia_ativa: bool = False

    # neurovascular
    enxaqueca_refrataria: bool = False
    hipertensao_resistente: bool = False
    dislipidemia_ldl_maior_190: bool = False
    hbA1c_maior_7_5: bool = False
    doencas_colageno: bool = False
    alcoolismo: bool = False
    uso_aco: bool = False
    histfam_coronariana: bool = False
    histfam_ateromatose_sist: bool = False
    histfam_avc_isquemico: bool = False
    histfam_aneurisma_intracraniano: bool = False

    # AAA/aneurismas gerais
    histfam_aaa: bool = False
    outro_aneurisma: bool = False
    transplantado: bool = False
