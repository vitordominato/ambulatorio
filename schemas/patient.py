from pydantic import BaseModel
from typing import List, Literal

class Patient(BaseModel):
    id: str
    name: str
    sex: Literal["M","F","I"]
    birth_date: str  # "YYYY-MM-DD"
    comorbidities: List[str] = []
    smoking_history_pack_years: int = 0
    is_health_worker: bool = False
    is_pregnant: bool = False

