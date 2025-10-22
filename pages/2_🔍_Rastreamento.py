# -*- coding: utf-8 -*-
# pages/2_🔎_Rastreamento.py

from __future__ import annotations
import os
import yaml
import pandas as pd
import streamlit as st

# componentes visuais (com fallback)
try:
    from components.reco_card import show_reco_card
    _HAS_RECO = True
except Exception:
    _HAS_RECO = False

try:
    from components.pdf_viewer import show_pdf
    _HAS_PDF = True
except Exception:
    _HAS_PDF = False

st.title("🔎 Rastreamento")

DATA_DIR = "data"
SCREENING_PATH = os.path.join(DATA_DIR, "screening_rules.yaml")
PDFS_INDEX_PATH = os.path.join(DATA_DIR, "pdfs_index.csv")

# ---------------- Utils ----------------
def load_yaml(path: str):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.error(f"Falha ao ler YAML `{path}`: {e}")
        return None

def load_csv(path: str) -> pd.DataFrame | None:
    if not os.path.isfile(path):
        return None
    try:
        return pd.read_csv(path, encoding="utf-8")
    except Exception as e:
        st.error(f"Falha ao ler CSV `{path}`: {e}")
        return None

def ctx_from_patient() -> dict:
    p = st.session_state.get("patient", {}) or {}
    sex = p.get("sex", "M")
    if sex not in ("M","F"):
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

def as_list(x):
    if x is None:
        return []
    if isinstance(x, (list, tuple)):
        return list(x)
    return [x]

# ------------- carregamento -------------
ctx = ctx_from_patient()
rules_data = load_yaml(SCREENING_PATH) or {}
rules = rules_data.get("screening_rules", [])

pdfs_df = load_csv(PDFS_INDEX_PATH)
if pdfs_df is None:
    pdfs_df = pd.DataFrame(columns=["id","title","category","path_local","url_remote","tags","condition"])
else:
    for col in ["category","condition","path_local","url_remote","title"]:
        if col not in pdfs_df.columns:
            pdfs_df[col] = ""
    pdfs_df = pdfs_df.fillna("")

# ------------- recomendações -------------
st.subheader("Recomendações de rastreio")

valid = []
for r in rules:
    if eval_condition(r.get("condition"), ctx):
        valid.append(r)

if not valid:
    st.warning("Nenhuma recomendação encontrada para o perfil atual. Ajuste os dados no **Cadastro do Paciente**.")
else:
    if not _HAS_RECO:
        st.info("Componente visual de recomendação indisponível — exibindo versão simples.")
    for i, r in enumerate(valid, start=1):
        title = r.get("title", f"Recomendação {i}")
        desc = r.get("description","")
        actions = as_list(r.get("actions"))
        refs = as_list(r.get("references"))

        if _HAS_RECO:
            show_reco_card({
                "title": title,
                "rationale": desc,
                "action": actions,
                "references": refs
            }, key_prefix=f"scr_{i}")
        else:
            st.markdown(f"### {title}")
            if desc: st.caption(desc)
            if actions:
                st.markdown("\n".join(f"- {a}" for a in actions))
            if refs:
                with st.expander("📚 Referências"):
                    st.markdown("\n".join(f"- {x}" for x in refs))
            st.divider()

# ------------- protocolos acionados (PDFs) -------------
# Mostra PDFs de categoria "Protocolo" cuja condição bate com o paciente (ex.: tabagismo → protocolo cardiológico)
st.subheader("Protocolos acionados")

if pdfs_df.empty:
    st.caption("Nenhum índice de protocolos em `data/pdfs_index.csv`.")
else:
    protos = pdfs_df[pdfs_df["category"].str.lower() == "protocolo"].copy()
    shown = False
    for _, row in protos.iterrows():
        if not eval_condition(str(row.get("condition") or ""), ctx):
            continue
        shown = True
        title = row.get("title","Protocolo")
        local_path = row.get("path_local") or ""
        url_remote = row.get("url_remote") or ""
        if _HAS_PDF:
            show_pdf(
                title=title,
                local_path=local_path if local_path else None,
                url=url_remote if url_remote else None,
                embed=False,
                key=f"proto_{row.get('id','')}"
            )
        else:
            st.markdown(f"**{title}**")
            if local_path and os.path.isfile(local_path):
                with open(local_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button("⬇️ Baixar PDF", data=pdf_bytes,
                                   file_name=os.path.basename(local_path),
                                   mime="application/pdf", use_container_width=True)
            if url_remote:
                st.link_button("🔗 Abrir PDF (online)", url=url_remote, use_container_width=True)
            st.divider()
    if not shown:
        st.caption("Nenhum protocolo condicional aplicável ao perfil atual.")
