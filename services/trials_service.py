# -*- coding: utf-8 -*-
# services/trials_service.py

from __future__ import annotations
import os
import yaml
from typing import Any, Dict, List
from schemas.patient import Patient


# ------------------------------------------------------------
# Utilidades básicas
# ------------------------------------------------------------
def load_trials(path: str = "data/trials.yaml") -> List[Dict[str, Any]]:
    """Lê o arquivo YAML de estudos clínicos."""
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("trials", [])
    except Exception:
        return []


def _eval_condition(expr: str | int | float | None, ctx: Dict[str, Any]) -> bool:
    """Avalia expressão booleana de forma segura (usada nas condições dos estudos)."""
    if expr is None or (isinstance(expr, str) and not expr.strip()):
        return True
    if isinstance(expr, (int, float)):
        return bool(expr)
    if isinstance(expr, str):
        try:
            return bool(eval(expr, {"__builtins__": None}, ctx))
        except Exception:
            return False
    return False


def _explain_condition(expr: str | None, ctx: Dict[str, Any]) -> List[str]:
    """Gera uma explicação simples dos motivos de elegibilidade."""
    if not isinstance(expr, str):
        return []
    tokens = set(
        t for t in (
            expr.replace("(", " ").replace(")", " ")
               .replace("and", " ").replace("or", " ")
               .replace("not", " ").split()
        )
        if t.isidentifier() and t in ctx
    )
    reasons = []
    for t in sorted(tokens):
        val = ctx.get(t)
        if isinstance(val, bool) and val:
            reasons.append(f"{t}=True")
        elif t == "sex":
            reasons.append(f"sex={ctx['sex']}")
        elif t == "age":
            reasons.append(f"age={ctx['age']}")
    return reasons


# ------------------------------------------------------------
# Função principal
# ------------------------------------------------------------
def eligible_trials(patient: Dict[str, Any] | Patient, trials: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Avalia cada estudo e retorna lista de estudos compatíveis com o perfil do paciente.
    O arquivo trials.yaml deve conter um campo 'condition' em cada bloco.
    """
    # Constrói o contexto de avaliação
    if isinstance(patient, Patient):
        ctx = patient.to_dict()
    else:
        p = patient or {}
        sex = p.get("sex", "M")
        if sex not in ("M", "F"):
            sex = "M"
        ctx = {"age": int(p.get("age", 0) or 0), "sex": sex}
        for k, v in p.items():
            if isinstance(v, bool):
                ctx[k] = v

    matches = []
    for t in trials:
        cond = t.get("condition")
        ok = _eval_condition(cond, ctx)
        if ok:
            t_copy = dict(t)
            t_copy["match_reasons"] = _explain_condition(str(cond or ""), ctx)
            matches.append(t_copy)
    return matches
