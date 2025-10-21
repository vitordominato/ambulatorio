# -*- coding: utf-8 -*-
# pages/3_💉_Vacinas.py

from __future__ import annotations
import os
import yaml
import pandas as pd
import streamlit as st

# --- Imports opcionais dos componentes (blindados) ---
try:
    from components.reco_card import show_reco_card
    _RECO_OK = True
except Exception:
    _RECO_OK = False

try:
    from components.pdf_viewer import show_pdf
    _PDF_OK = True
except Exception:
    _PDF_OK = False

st.title("💉 Vacinas")

# ---------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------
DATA_DIR = "data"
VAX_RULES_PATH = os.path.join(DATA_DIR, "vaccines_rules.yaml")
PDFS_INDEX_PATH = os.path.join(DATA_DIR, "pdfs_index.csv")

def load_yaml(path: str) -> dict | list | None:
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

def build_context() -> dict:
    """Cria o 'contexto' para avaliar condições de regras (age, sex e fatores booleanos)."""
    patient = st.session_state.get("patient", {})
    # saneamento básico
    sex = patient.get("sex", "M")
    if sex not in ("M", "F"):
        sex = "M"
    ctx = {"age": int(patient.get("age", 0) or 0), "sex": sex}

    # adiciona todos os booleanos do dict do paciente ao contexto
    for k, v in patient.items():
        if isinstance(v, bool):
            ctx[k] = v
    return ctx

def eval_condition(expr: str | float | int | None, ctx: dict) -> bool:
    """Avalia a expressão booleana de forma restrita ao contexto fornecido."""
    if expr is None:
        return True
    if isinstance(expr, (int, float)):
        return bool(expr)
    if isinstance(expr, str):
        e = expr.strip()
        if not e:
            return True
        try:
            # Somente variáveis do ctx, sem builtins.
            return bool(eval(e, {"__builtins__": None}, ctx))
        except Exception:
            # condição inválida -> considera falso para segurança
            return False
    return False

def as_list(x):
    if x is None:
        return []
    if isinstance(x, (list, tuple)):
        return list(x)
    return [x]

# ---------------------------------------------------------------------
# Carregamento dos dados
# ---------------------------------------------------------------------
ctx = build_context()

data = load_yaml(VAX_RULES_PATH)
if not data or "vaccines_rules" not in data:
    st.info("Regras de vacinas não encontradas. Verifique `data/vaccines_rules.yaml`.")
    data = {"vaccines_rules": []}

df_pdfs = load_csv(PDFS_INDEX_PATH)
if df_pdfs is None:
    df_pdfs = pd.DataFrame(columns=["id", "title", "category", "path_local", "url_remote", "tags", "condition"])

# ---------------------------------------------------------------------
# Recomendações de Vacinas
# ---------------------------------------------------------------------
st.subheader("Recomendações")

rules = data.get("vaccines_rules", [])
valid_rules = []
for rule in rules:
    cond = rule.get("condition")
    if eval_condition(cond, ctx):
        valid_rules.append(rule)

if not valid_rules:
    st.warning("Nenhuma recomendação encontrada para o perfil atual. Ajuste os dados no **Cadastro do Paciente**.")
else:
    if not _RECO_OK:
        st.info("Componente visual de recomendação indisponível. Exibindo versão simples.")
    for i, rule in enumerate(valid_rules, start=1):
        title = rule.get("title", f"Recomendação {i}")
        schedule = as_list(rule.get("schedule"))
        notes = as_list(rule.get("notes"))
        contraind = as_list(rule.get("contraindications"))
        refs = as_list(rule.get("references"))

        # monta um texto mais clínico para o cartão
        action_text = []
        if schedule:
            action_text.extend(schedule)
        if contraind:
            action_text.append("**Contraindicações**")
            action_text.extend([f"- {c}" for c in contraind])

        if _RECO_OK:
            show_reco_card({
                "title": title,
                "rationale": rule.get("description", ""),
                "action": action_text,
                "notes": notes,
                "references": refs
            }, key_prefix=f"vax_{i}")
        else:
            # fallback simples
            st.markdown(f"### {title}")
            if rule.get("description"):
                st.caption(rule["description"])
            if action_text:
                st.markdown("\n".join([f"- {line}" if not line.startswith("**") else line for line in action_text]))
            if notes:
                with st.expander("Observações"):
                    st.markdown("\n".join([f"- {n}" for n in notes]))
            if refs:
                with st.expander("📚 Referências"):
                    st.markdown("\n".join([f"- {r}" for r in refs]))
            st.divider()

# ---------------------------------------------------------------------
# PDFs relacionados a Vacinas (condicionais)
# ---------------------------------------------------------------------
st.subheader("Documentos úteis (Vacinas)")

if df_pdfs.empty:
    st.caption("Nenhum índice de PDFs encontrado em `data/pdfs_index.csv`.")
else:
    # Mantém apenas categoria Vacinas (ou diretrizes de imunização, se desejar inclua 'Diretriz')
    sub = df_pdfs[df_pdfs["category"].fillna("").str.lower().isin(["vacinas"])]
    if sub.empty:
        st.caption("Não há itens de categoria 'Vacinas' no índice de PDFs.")
    else:
        any_shown = False
        for _, row in sub.iterrows():
            cond_expr = str(row.get("condition") or "").strip()
            ok = eval_condition(cond_expr, ctx)
            if not ok:
                continue
            any_shown = True
            title = row.get("title", "Documento")
            path_local = row.get("path_local") or ""
            url_remote = row.get("url_remote") or ""

            if _PDF_OK:
                show_pdf(
                    title=title,
                    local_path=path_local if path_local else None,
                    url=url_remote if url_remote else None,
                    embed=False,
                    key=f"pdf_{row.get('id','')}"
                )
            else:
                # fallback: apenas links/avisos
                st.markdown(f"**{title}**")
                if path_local and os.path.isfile(path_local):
                    st.caption(f"• Arquivo local: `{path_local}` (download disponível na aba Biblioteca de PDFs).")
                if url_remote:
                    st.markdown(f"[Abrir online]({url_remote})")
                st.divider()

        if not any_shown:
            st.caption("Nenhum documento de vacinas se aplica ao perfil atual.")
