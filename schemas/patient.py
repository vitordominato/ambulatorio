from pydantic import BaseModel
from typing import List, Literal

class Patient(BaseModel):
    id: str
    sex: Literal["M","F","I"]
    age: int
    comorbidities: List[str] = []
    is_health_worker: bool = False

    # fatores/antecedentes
    imc_ge_25: bool = False
    smoker_or_ex: bool = False
    is_pregnant: bool = False  # 'gestante' no formulário
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

    # neurovascular (se em uso)
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

    # AAA/aneurismas
    histfam_aaa: bool = False
    outro_aneurisma: bool = False
    transplantado: bool = False

