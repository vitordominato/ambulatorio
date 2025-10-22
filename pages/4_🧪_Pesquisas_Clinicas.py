# -*- coding: utf-8 -*-
# pages/4_🔬_Pesquisas_Clinicas.py

from __future__ import annotations
import os
import yaml
import streamlit as st

st.title("🔬 Pesquisas Clínicas – Elegibilidade")

DATA_DIR = "data"
TRIALS_PATH = os.path.join(DATA_DIR, "trials.yaml")

# ---------------------------
# Utils
# ---------------------------
def load_trials_yaml(path: str) -> list[dict]:
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("trials", [])
    except Exception as e:
        st.error(f"Falha ao ler `{path}`: {e}")
        return []

def build_ctx() -> dict:
    """Cria o contexto com age, sex e todos os booleanos do paciente."""
    p = st.session_state.get("patient", {}) or {}
    sex = p.get("sex", "M")
    if sex not in ("M", "F"):
        sex = "M"
    ctx = {"age": int(p.get("age", 0) or 0), "sex": sex}
    for k, v in p.items():
        if isinstance(v, bool):
            ctx[k] = v
    return ctx

def eval_condition(expr: str | int | float | None, ctx: dict) -> bool:
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

def explain_match(expr: str, ctx: dict) -> list[str]:
    """
    Explicação simples: lista variáveis/termos do contexto que avaliam como True.
    (não é um parser lógico completo, mas ajuda o clínico a entender o porquê)
    """
    if not isinstance(expr, str):
        return []
    tokens = set(
        t for t in (
            expr.replace("(", " ").replace(")", " ")
               .replace("and", " ").replace("or", " ")
               .replace("not", " ").replace(">", " > ")
               .replace("<", " < ").replace("==", " == ").split()
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

# ---------------------------
# Flow
# ---------------------------
patient = st.session_state.get("patient")
if not patient:
    st.warning("Cadastre um paciente primeiro.")
    st.stop()

ctx = build_ctx()
trials = load_trials_yaml(TRIALS_PATH)

if not trials:
    st.info("Nenhum cadastro de estudo encontrado em `data/trials.yaml`.\n\n"
            "Quando houver estudos ativos, adicione-os neste arquivo.")
    st.stop()

matches = []
for t in trials:
    cond = t.get("condition")
    ok = eval_condition(cond, ctx)
    if ok:
        t = dict(t)  # cópia
        t["match_reasons"] = explain_match(str(cond or ""), ctx)
        matches.append(t)

if not matches:
    st.info("Sem estudos elegíveis para o perfil atual.")
else:
    st.success(f"Encontradas **{len(matches)}** possibilidades.")
    for t in matches:
        with st.container(border=True):
            st.markdown(f"### {t.get('title','Estudo')}")
            meta = []
            if t.get("phase"):
                meta.append(t["phase"])
            if t.get("disease_area"):
                meta.append(t["disease_area"])
            if meta:
                st.caption(" • ".join(meta))

            # Motivos do match (simples)
            reasons = t.get("match_reasons") or []
            if reasons:
                st.markdown("**Motivos do match:** " + ", ".join(reasons))

            # Critérios adicionais
            inc = t.get("inclusion") or []
            exc = t.get("exclusion") or []
            if inc:
                with st.expander("✅ Critérios de inclusão"):
                    st.markdown("\n".join(f"- {i}" for i in inc))
            if exc:
                with st.expander("🚫 Critérios de exclusão"):
                    st.markdown("\n".join(f"- {i}" for i in exc))

            # Centros e contato
            sites = t.get("sites") or []
            if sites:
                with st.expander("📍 Centros participantes / Contato"):
                    for s in sites:
                        line = " - " + s.get("name", "Centro")
                        if s.get("city"):
                            line += f" — {s['city']}"
                        st.markdown(line)
                        if s.get("contact"):
                            st.caption(f"   Contato: {s['contact']}")

            # Referências
            refs = t.get("references") or []
            if refs:
                with st.expander("📚 Referências"):
                    st.markdown("\n".join(f"- {r}" for r in refs))

