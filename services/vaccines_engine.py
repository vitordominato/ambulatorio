# -*- coding: utf-8 -*-
# services/vaccines_engine.py

from __future__ import annotations
import os
from typing import Any, Dict, List, Tuple
import yaml


DATA_PATH = "data/vaccines_rules.yaml"


# ----------------------------- utils -----------------------------
def _safe_load_yaml(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _ctx_from_patient(patient: Dict[str, Any]) -> Dict[str, Any]:
    """Contexto disponível para avaliar as condições das regras."""
    p = patient or {}
    sex = (p.get("sex") or "M").upper()
    if sex not in ("M", "F"):
        sex = "M"
    ctx: Dict[str, Any] = {
        "age": int(p.get("age", 0) or 0),
        "sex": sex,
    }
    for k, v in p.items():
        if isinstance(v, bool):
            ctx[k] = v
    return ctx


def _eval_condition(expr: Any, ctx: Dict[str, Any]) -> bool:
    """Avalia a expressão booleana de condição, restrita ao contexto fornecido."""
    if expr is None:
        return True
    if isinstance(expr, (int, float)):
        return bool(expr)
    if isinstance(expr, str):
        e = expr.strip()
        if not e:
            return True
        try:
            return bool(eval(e, {"__builtins__": None}, ctx))
        except Exception:
            return False
    return False


def _why(expr: Any, ctx: Dict[str, Any]) -> List[str]:
    """Gera uma explicação simples dos motivos (variáveis True no contexto)."""
    if not isinstance(expr, str):
        return []
    tokens = set(
        t for t in (
            expr.replace("(", " ").replace(")", " ")
               .replace("and", " ").replace("or", " ")
               .replace("not", " ").replace(">=", " >= ")
               .replace("<=", " <= ").replace("==", " == ")
               .replace(">", " > ").replace("<", " < ").split()
        )
        if t.isidentifier() and t in ctx
    )
    out: List[str] = []
    for t in sorted(tokens):
        val = ctx.get(t)
        if isinstance(val, bool) and val:
            out.append(f"{t}=True")
        elif t in ("age", "sex"):
            out.append(f"{t}={ctx[t]}")
    return out


# ----------------------------- API -----------------------------
def load_rules(path: str = DATA_PATH) -> List[Dict[str, Any]]:
    """
    Lê o arquivo data/vaccines_rules.yaml e devolve a lista de regras.
    Aceita também um formato legado (dict por vacina) e o converte.
    """
    data = _safe_load_yaml(path)
    if not data:
        return []

    # formato novo (recomendado)
    if isinstance(data.get("vaccines_rules"), list):
        return data["vaccines_rules"]

    # formato legado (dict por vacina) -> converte em lista
    rules: List[Dict[str, Any]] = []
    if isinstance(data, dict):
        for key, v in data.items():
            if not isinstance(v, dict):
                continue
            rules.append({
                "id": key,
                "title": v.get("label", key),
                "condition": v.get("rules", ""),
                "schedule": v.get("schedule", []),
                "contraindications": v.get("contraindications", []),
                "references": v.get("refs", []),
                "notes": v.get("notes", []),
            })
    return rules


def suggest_vaccines(patient: Dict[str, Any], rules: List[Dict[str, Any]] | None = None
                     ) -> List[Dict[str, Any]]:
    """
    Avalia as regras de vacinação para um paciente.
    Retorna uma lista de recomendações já normalizadas com chaves:
      - title, rationale, action (lista), contraindications (lista),
        references (lista), notes (lista), id
    """
    if rules is None:
        rules = load_rules()

    ctx = _ctx_from_patient(patient)
    recs: List[Dict[str, Any]] = []

    for rule in rules:
        cond = rule.get("condition")
        if not _eval_condition(cond, ctx):
            continue

        # Normaliza campos
        title = rule.get("title") or rule.get("label") or "Vacina"
        description = rule.get("description", "")
        schedule = rule.get("schedule") or []
        schedule = schedule if isinstance(schedule, list) else [schedule]
        contraind = rule.get("contraindications") or []
        contraind = contraind if isinstance(contraind, list) else [contraind]
        refs = rule.get("references") or rule.get("refs") or []
        refs = refs if isinstance(refs, list) else [refs]
        notes = rule.get("notes") or []
        notes = notes if isinstance(notes, list) else [notes]

        action = list(schedule)
        if contraind:
            action.append("**Contraindicações**")
            action.extend([f"- {c}" for c in contraind])

        recs.append({
            "id": rule.get("id", title.lower().replace(" ", "_")),
            "title": title,
            "rationale": description,
            "action": action,
            "contraindications": contraind,
            "references": refs,
            "notes": notes,
            "why": _why(cond, ctx),
        })

    return recs
