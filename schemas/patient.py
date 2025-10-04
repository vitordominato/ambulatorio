from pydantic import BaseModel
from typing import List, Literal

class Patient(BaseModel):
    id: str
    name: str
    sex: Literal["M","F","I"]
    age: int
    comorbidities: List[str] = []
    smoking_status: Literal["Não", "Sim", "Ex-tabagista", "Passivo"] = "Não"
    is_health_worker: bool = False
    # fatores clínicos
    imc_ge_25: bool = False
    smoker_or_ex: bool = False
    is_pregnant: bool = False
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


