# -*- coding: utf-8 -*-
# services/rules_engine.py
from __future__ import annotations
from typing import List, Dict
from dataclasses import dataclass, field
from schemas.patient import Patient


@dataclass
class Recommendation:
    code: str
    title: str
    rationale: str
    action: str
    notes: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)


# -------------------------------------------------------
# REGRAS CLÍNICAS — não vacinais, compatíveis com schema
# -------------------------------------------------------
def rule_aaa_screening(p: Patient) -> List[Recommendation]:
    """Rastreamento de aneurisma de aorta abdominal."""
    recs = []
    risco_homens = (p.sex == "M" and 65 <= p.age <= 75 and p.smoker_or_ex)
    risco_familiar = (p.hist_aaa and p.age >= 65)
    if risco_homens or risco_familiar:
        recs.append(Recommendation(
            code="SCR_AAA",
            title="Rastreamento de Aneurisma de Aorta Abdominal (AAA)",
            rationale="Homens 65–75 anos com tabagismo prévio e/ou histórico familiar têm risco aumentado.",
            action="Solicitar ultrassonografia abdominal única para rastreio de AAA.",
            references=[
                "Diretrizes Brasileiras de Doença Aneurismática – SBACV 2021",
                "USPSTF AAA Screening 2021"
            ]
        ))
    return recs


def rule_ldl190_flag(p: Patient) -> List[Recommendation]:
    """Alerta para LDL elevado (dislipidemia grave)."""
    if not p.dislipidemia_ldl190:
        return []
    return [Recommendation(
        code="FLAG_LDL190",
        title="LDL ≥ 190 mg/dL – Suspeitar Hipercolesterolemia Familiar",
        rationale="LDL muito elevado sugere hipercolesterolemia familiar (HF) e risco cardiovascular aumentado.",
        action=(
            "Repetir perfil lipídico; investigar DAC precoce na família; "
            "considerar escore Dutch Lipid Clinic; encaminhar a especialista."
        ),
        references=["ACC/AHA 2019 – Cholesterol Management", "SBPC/ML 2023 – HF Consensus"]
    )]


def rule_aco_migraine(p: Patient) -> List[Recommendation]:
    """Uso de ACO + enxaqueca: risco de AVC."""
    if not (p.contraceptivo_oral and p.migranea_refrataria and p.sex == "F"):
        return []
    return [Recommendation(
        code="ALERTA_ACO_MIGRAINE",
        title="Uso de ACO e Enxaqueca – Avaliar presença de aura",
        rationale="ACO combinado pode ser contra-indicado em enxaqueca com aura, aumentando risco de AVC.",
        action="Investigar presença de aura, idade e tabagismo. Considerar método não estrogênico.",
        references=["Diretrizes de Contracepção e Enxaqueca – FEBRASGO 2023"]
    )]


def rule_immunosuppressed_bundle(p: Patient) -> List[Recommendation]:
    """Alertas gerais para imunossuprimidos e transplantados."""
    if not (p.imunossuprimido or p.transplantado):
        return []
    return [Recommendation(
        code="ALERTA_IMUNO_VACINAS_VIVAS",
        title="Evitar vacinas vivas em imunossuprimidos/transplantados",
        rationale="Pacientes imunossuprimidos têm risco de doença vacinal/disseminada.",
        action="Evitar MMR, Varicela, Febre Amarela e outras vacinas vivas enquanto durar imunossupressão.",
        notes=["Avaliar janela segura pós-transplante conforme protocolo institucional."],
        references=["MS/PNI 2024 – Precauções Vacinais", "SBIm 2024 – Calendário Adulto"]
    )]


# -------------------------------------------------------
# MOTOR DE EXECUÇÃO
# -------------------------------------------------------
class RulesEngine:
    """Executa todas as regras clínicas não vacinais."""
    def __init__(self):
        self.rules = [
            rule_aaa_screening,
            rule_ldl190_flag,
            rule_aco_migraine,
            rule_immunosuppressed_bundle,
        ]

    def evaluate(self, patient: Patient) -> List[Recommendation]:
        recs: List[Recommendation] = []
        for rule in self.rules:
            recs.extend(rule(patient))
        return recs


# -------------------------------------------------------
# Helper p/ renderização no app
# -------------------------------------------------------
def render_recommendation(r: Recommendation) -> Dict[str, str]:
    return {
        "title": r.title,
        "rationale": r.rationale,
        "action": r.action,
        "notes": "\n".join(f"- {n}" for n in r.notes),
        "references": "\n".join(f"• {ref}" for ref in r.references)
    }
