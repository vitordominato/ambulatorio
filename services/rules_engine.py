# services/rules_engine.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
import yaml, unicodedata, re, pathlib

from schemas.patient import Patient

# --------------------------------------------
# Data holders
# --------------------------------------------
@dataclass
class Reference:
    label: str
    pdf_id: str
    url: Optional[str] = None

@dataclass
class Recommendation:
    code: str
    title: str
    rationale: str
    action: str
    notes: List[str] = field(default_factory=list)
    references: List[Reference] = field(default_factory=list)
    schedule_key: Optional[str] = None

@dataclass
class EngineOutput:
    patient_id: str
    recommendations: List[Recommendation]
    no_recommendation_message: Optional[str] = None

# --------------------------------------------
# Load YAML (SCHEDULES, VAX_META, REFS_URLS)
# --------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "data" / "vaccines_rules.yaml"

with open(YAML_PATH, "r", encoding="utf-8") as f:
    __CFG = yaml.safe_load(f)

SCHEDULES: Dict[str, Dict[str, str]] = __CFG.get("SCHEDULES", {})
VAX_META: Dict[str, Dict[str, object]] = __CFG.get("VAX_META", {})
REFS_URLS: Dict[str, str] = __CFG.get("REFS_URLS", {})

# --------------------------------------------
# Utils / synonyms (para futuro uso em texto livre)
# --------------------------------------------
_SYNONYMS = {
    "cancer": {"cancer", "câncer", "ca", "neoplasia", "adenocarcinoma", "carcinoma"},
    "diabetes": {"diabetes", "dm", "mellitus", "diabete"},
    "dpoc": {"dpoc", "doença pulmonar obstrutiva", "bronquite cronica"},
    "gestante": {"gestante", "grávida", "gravida", "gestacao", "gestação"},
}
def _strip_accents_lower(t: str) -> str:
    t = unicodedata.normalize('NFD', t)
    return "".join(ch for ch in t if unicodedata.category(ch) != "Mn").lower()

# --------------------------------------------
# Builders
# --------------------------------------------
Rule = Callable[[Patient], List[Recommendation]]

def _ref(label: str, pdf_id: str) -> Reference:
    return Reference(label=label, pdf_id=pdf_id, url=REFS_URLS.get(pdf_id))

def make_vax(code: str, title: str, rationale: str, action: str,
             schedule_key: Optional[str] = None,
             notes: Optional[List[str]] = None,
             refs: Optional[List[Reference]] = None) -> Recommendation:
    # schedule_key pode vir de VAX_META (padroniza)
    if code in VAX_META and VAX_META[code].get("schedule_key"):
        schedule_key = VAX_META[code]["schedule_key"]  # type: ignore
    return Recommendation(code=code, title=title, rationale=rationale,
                          action=action, schedule_key=schedule_key,
                          notes=notes or [], references=refs or [])

# --------------------------------------------
# Regras VACINA
# --------------------------------------------
def rule_health_worker_bundle(p: Patient) -> List[Recommendation]:
    if not p.is_health_worker:
        return []
    return [
        make_vax("VAC_HEPB", "Hepatite B",
                 "Profissional de saúde com risco ocupacional.",
                 "Completar esquema (checar doses prévias e considerar anti-HBs após série)."),
        make_vax("VAC_DTPA", "dTpa",
                 "Reforço para proteção individual e de pacientes vulneráveis.",
                 "Aplicar reforço conforme calendário do adulto; gestantes: uma dose por gestação."),
        make_vax("VAC_INFLUENZA", "Influenza (anual)",
                 "Risco ocupacional e proteção de pacientes.",
                 "Vacinar anualmente."),
        make_vax("VAC_COVID19", "COVID-19",
                 "Risco ocupacional em serviços de saúde.",
                 "Seguir recomendações vigentes de reforço por idade/risco."),
        make_vax("VAC_MMR_VAR", "Tríplice viral e Varicela",
                 "Sem comprovação vacinal prévia/sorologia.",
                 "Verificar histórico/sorologia e atualizar.",
                 notes=["Contraindicações em gestantes/imunossuprimidos."]),
    ]

def rule_age_based_adult_core(p: Patient) -> List[Recommendation]:
    return [
        make_vax("VAC_INFLUENZA", "Influenza (anual)",
                 "Reduz risco de gripe e complicações.",
                 "Vacinar anualmente."),
        make_vax("VAC_COVID19", "COVID-19",
                 "Proteção contra formas graves.",
                 "Indicar reforço conforme idade/risco."),
        make_vax("VAC_DTPA", "dT/dTpa",
                 "Manter proteção contra tétano, difteria e coqueluche.",
                 "Aplicar reforço conforme calendário; dTpa em gestantes."),
    ]

def rule_conditions_risk_bundles(p: Patient) -> List[Recommendation]:
    recs: List[Recommendation] = []
    if any([p.dpoc, p.renal_cronica, p.hepatica_cronica, p.cardiovascular_cronica, p.imunossuprimido]):
        recs.append(make_vax("VAC_PNEUMO", "Pneumocócicas (condições de risco)",
                             "Condições crônicas aumentam risco de doença pneumocócica invasiva.",
                             "Seguir esquema para grupos de risco."))
    if p.age <= 26:
        recs.append(make_vax("VAC_HPV", "HPV",
                             "Proteção contra infecção por HPV e neoplasias associadas.",
                             "Indicar conforme elegibilidade (idade/sexo) e completar esquema."))
    return recs

def rule_dengue_contextual(p: Patient) -> List[Recommendation]:
    return [make_vax("VAC_DENGUE", "Dengue (Qdenga)",
                     "Contexto epidemiológico e elegibilidade conforme norma nacional.",
                     "Avaliar elegibilidade e aplicar esquema.")]

# --------------------------------------------
# Regras CLÍNICAS (não-vacinais) visíveis no mesmo feed
# --------------------------------------------
def rule_aaa_screening(p: Patient) -> List[Recommendation]:
    recs: List[Recommendation] = []
    homem_tabagista = (p.sex == "M" and 65 <= p.age <= 75 and p.smoker_or_ex)
    famhx = (p.famhx_aaa and p.age >= 65)
    if homem_tabagista or famhx:
        recs.append(Recommendation(
            code="SCR_AAA",
            title="Rastreamento de aneurisma de aorta abdominal (USG)",
            rationale="Perfil com risco aumentado (sexo/idade/tabagismo e/ou histórico familiar).",
            action="Solicitar/avaliar USG de aorta abdominal conforme protocolo vigente.",
            references=[_ref("Diretrizes de rastreio de AAA", "DIRETRIZ_AAA_VIGENTE")]
        ))
    return recs

def rule_ldl190_fh(p: Patient) -> List[Recommendation]:
    if not p.ldl_maior_190:
        return []
    return [Recommendation(
        code="FLAG_LDL190",
        title="LDL ≥ 190 mg/dL — suspeitar hipercolesterolemia familiar",
        rationale="LDL muito elevado eleva risco cardiovascular e pode indicar HF.",
        action=("Repetir perfil lipídico; investigar DAC precoce na família; considerar Dutch Lipid Clinic; "
                "encaminhar para avaliação especializada."),
        references=[_ref("Consenso Hipercolesterolemia Familiar", "CONSENSO_HF_VIGENTE")]
    )]

def rule_immunosuppressed_bundle(p: Patient) -> List[Recommendation]:
    if not (p.imunossuprimido or p.transplantado):
        return []
    recs = [
        make_vax("VAC_PNEUMO_IMUNO", "Pneumocócicas (imunossuprimidos/transplantados)",
                 "Risco elevado de doença pneumocócica invasiva.",
                 "Aplicar esquema específico para imunossuprimidos/transplantados."),
        make_vax("VAC_INFLUENZA_IMUNO", "Influenza (anual)",
                 "Imunossupressão aumenta complicações por influenza.",
                 "Vacinar anualmente."),
        make_vax("VAC_COVID19_IMUNO", "COVID-19",
                 "Maior risco de formas graves em imunossuprimidos.",
                 "Aplicar reforços conforme norma específica."),
        make_vax("VAC_HEPB_IMUNO", "Hepatite B",
                 "Maior risco e pior evolução em imunossuprimidos.",
                 "Completar esquema e avaliar resposta sorológica quando indicado."),
        Recommendation(
            code="ALERTA_VACINAS_VIVAS",
            title="Evitar vacinas VIVAS em imunossuprimidos",
            rationale="Risco de doença vacinal/disseminada.",
            action="Evitar MMR/Varicela/Febre Amarela e outras vivas enquanto durar a imunossupressão.",
            notes=["Transplante recente: seguir janelas específicas do protocolo do serviço."],
            references=[_ref("Calendário do Adulto — precauções", "MS_CAL_ADULTO_2024")]
        )
    ]
    return recs

def rule_aco_migraine_safety(p: Patient) -> List[Recommendation]:
    if not p.uso_aco and not p.enxaqueca_refrataria:
        return []
    if p.uso_aco and p.sex == "F" and p.enxaqueca_refrataria:
        return [Recommendation(
            code="ALERTA_ACO_MIGRAINE",
            title="Uso de ACO e enxaqueca — avaliar presença de aura",
            rationale="ACO combinado pode ser contra-indicado em enxaqueca com aura (risco de AVC).",
            action=("Investigar aura, idade, tabagismo e fatores adicionais. "
                    "Considerar método não estrogênico/progestagênico isolado se aura presente."),
            references=[_ref("Diretrizes de contracepção e enxaqueca", "DIRETRIZ_ACO_ENXAQUECA_VIGENTE")]
        )]
    return []

# --------------------------------------------
# Engine
# --------------------------------------------
class RulesEngine:
    def __init__(self) -> None:
        self.rules: List[Rule] = [
            rule_health_worker_bundle,
            rule_age_based_adult_core,
            rule_conditions_risk_bundles,
            rule_aaa_screening,
            rule_ldl190_fh,
            rule_immunosuppressed_bundle,
            rule_aco_migraine_safety,
            rule_dengue_contextual,
        ]

    # prioridade por vacina (para ordenar e resolver duplicidade por code)
    def _priority(self, rec: Recommendation) -> int:
        return int(VAX_META.get(rec.code, {}).get("priority", 50))

    def _sus(self, rec: Recommendation) -> Optional[bool]:
        meta = VAX_META.get(rec.code, {})
        val = meta.get("sus_available")
        return bool(val) if isinstance(val, bool) else None

    def _contra(self, rec: Recommendation) -> List[str]:
        return list(VAX_META.get(rec.code, {}).get("contraindications", []))

    def evaluate(self, p: Patient) -> EngineOutput:
        all_recs: List[Recommendation] = []
        for rule in self.rules:
            all_recs.extend(rule(p))

        # Deduplicação por code (mantém a de maior prioridade) e mescla notas/refs
        best: Dict[str, Recommendation] = {}
        for r in all_recs:
            key = r.code
            cur = best.get(key)
            if cur is None or self._priority(r) > self._priority(cur):
                best[key] = r
            else:
                cur.notes.extend([n for n in r.notes if n not in cur.notes])
                for ref in r.references:
                    if all(ref.pdf_id != rr.pdf_id for rr in cur.references):
                        cur.references.append(ref)

        if not best:
            return EngineOutput(p.id, [], "Nenhuma recomendação específica no momento.")

        ordered = sorted(best.values(), key=lambda r: (-self._priority(r), r.title))

        # Enriquecer notas com contraindicações, SUS e anexar doses/observ
        for r in ordered:
            contras = self._contra(r)
            if contras:
                r.notes.append("Contraindicações: " + "; ".join(contras))
            sus = self._sus(r)
            if sus is not None:
                r.notes.append(f"Disponível no SUS: {'Sim' if sus else 'Não'}")
            if r.schedule_key:
                sched = SCHEDULES.get(r.schedule_key, {})
                doses = sched.get("doses", "")
                obs = sched.get("observ", "")
                if doses:
                    r.action += f"\n\n**Doses:** {doses}"
                if obs:
                    r.notes.append(obs)

        return EngineOutput(p.id, ordered)

# --------------------------------------------
# Render helper (para UI)
# --------------------------------------------
def render_recommendation(r: Recommendation, highlight: bool = False) -> Dict[str, str]:
    refs = [f"• {ref.label} — {ref.url or '#'}" for ref in r.references]
    notes = [f"- {n}" for n in r.notes]
    title = f"🟢 Iniciar por aqui — {r.title}" if highlight else r.title
    return {
        "title": title,
        "rationale": r.rationale,
        "action": r.action,
        "notes": "\n".join(notes),
        "references": "\n".join(refs)
    }
