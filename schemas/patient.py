# -*- coding: utf-8 -*-
# schemas/patient.py

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict


@dataclass
class Patient:
    # Básicos
    id: str
    sex: str                  # "M" ou "F"
    age: int
    is_health_worker: bool = False

    # Fatores clínicos / antecedentes (padronizados)
    imc_ge_25: bool = False
    is_pregnant: bool = False
    smoker_or_ex: bool = False

    dm: bool = False
    dpoc: bool = False
    imunossuprimido: bool = False
    cardiovascular_cronica: bool = False
    renal_cronica: bool = False
    hepatica_cronica: bool = False
    neoplasia_ativa: bool = False

    dislipidemia_ldl190: bool = False
    hipertensao_resistente: bool = False
    migranea_refrataria: bool = False
    colageno_tecido: bool = False
    contraceptivo_oral: bool = False
    alcoolismo: bool = False
    transplantado: bool = False

    # Histórico familiar (prefixo hist_)
    famhx_mama: bool = False
    famhx_prostata: bool = False
    famhx_colorretal: bool = False
    hist_coronaria: bool = False
    hist_avc_isquemico: bool = False
    hist_aaa: bool = False
    hist_ateromatose: bool = False
    hist_intracr: bool = False
    outro_aneurisma: bool = False

    # Campo livre
    notes: str = ""

    # --------------------------
    # Helpers
    # --------------------------
    @staticmethod
    def _sanitize_sex(value: str) -> str:
        v = (value or "M").upper()
        return "F" if v == "F" else "M"

    @classmethod
    def normalize(cls, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza um dicionário possivelmente vindo de versões antigas do app
        para o formato padronizado atual.
        """
        d = dict(raw or {})

        # sexo apenas M/F
        d["sex"] = cls._sanitize_sex(d.get("sex", "M"))

        # renomes (legado → atual)
        renames = {
            # clínicos
            "ldl_maior_190": "dislipidemia_ldl190",
            "dm_hba1c_maior_75": "dm",  # antiga duplicata -> mantemos apenas 'dm'
            "enxaqueca_refrataria": "migranea_refrataria",
            "doencas_colageno": "colageno_tecido",
            "uso_aco": "contraceptivo_oral",
            "free_text": "notes",

            # históricos familiares (fam->hist quando aplicável)
            "famhx_coronariana": "hist_coronaria",
            "famhx_ateromatose": "hist_ateromatose",
            "famhx_avc_isquemico": "hist_avc_isquemico",
            "famhx_aaa": "hist_aaa",
            "famhx_an_intracraniano": "hist_intracr",
            "famhx_outro_aneurisma": "outro_aneurisma",
        }
        for old, new in renames.items():
            if old in d and new not in d:
                d[new] = d.get(old)

        # garante presença de todas as chaves esperadas com tipos corretos
        template = asdict(
            Patient(
                id=str(d.get("id", "")),
                sex=d.get("sex", "M"),
                age=int(d.get("age", 0) or 0),
                is_health_worker=bool(d.get("is_health_worker", False)),
            )
        )
        # inclui campos booleanos restantes do template
        for k in template.keys():
            if k in ("id", "sex", "age", "is_health_worker"):
                continue
            template[k] = bool(d.get(k, template[k]))

        # campos básicos (id/age/sex)
        template["id"] = str(d.get("id", ""))
        template["age"] = int(d.get("age", 0) or 0)
        template["sex"] = cls._sanitize_sex(d.get("sex", "M"))
        template["is_health_worker"] = bool(d.get("is_health_worker", False))

        # notes (string)
        template["notes"] = str(d.get("notes", ""))

        return template

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "Patient":
        norm = cls.normalize(raw)
        return cls(**norm)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["sex"] = self._sanitize_sex(d.get("sex", "M"))
        # garante tipos simples (int/bool/str)
        d["age"] = int(d.get("age", 0) or 0)
        for k, v in list(d.items()):
            if isinstance(v, bool):
                d[k] = bool(v)
            elif isinstance(v, int):
                d[k] = int(v)
            elif v is None:
                d[k] = False if "hist_" in k or k.endswith(("_cronica", "_refrataria")) else ""
        return d
