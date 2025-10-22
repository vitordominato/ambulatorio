# -*- coding: utf-8 -*-
# pages/5_📚_Biblioteca_PDFs.py

from __future__ import annotations
import os
import glob
import pandas as pd
import streamlit as st

# --- componente opcional para visualização elegante ---
try:
    from components.pdf_viewer import show_pdf
    _HAS_PDF_VIEW = True
except Exception:
    _HAS_PDF_VIEW = False

st.title("📚 Biblioteca de Guias e Protocolos")

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "pdfs_index.csv")

# -----------------------------------------------------------
# Utils
# -----------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def list_all_local_pdfs() -> list[dict]:
    """Lista TODOS os PDFs do repositório (fallback visual)."""
    files = sorted(glob.glob("**/*.pdf", recursive=True))
    out = []
    for p in files:
        if any(x in p.split(os.sep) for x in [".venv", "venv", ".git", "__pycache__"]):
            continue
        out.append({"title": os.path.basename(p), "path_local": p, "url_remote": "", "category": "", "tags": ""})
    return out

def _safe_read_csv(path: str) -> pd.DataFrame | None:
    if not os.path.isfile(path):
        return None
    try:
        df = pd.read_csv(path, encoding="utf-8")
        for col in ["id", "title", "category", "path_local", "url_remote", "tags", "condition"]:
            if col not in df.columns:
                df[col] = ""
        return df.fillna("")
    except Exception as e:
        st.error(f"Erro ao ler `{path}`: {e}")
        return None

def build_ctx() -> dict:
    """Contexto para avaliar 'condition' (usa estado do paciente)."""
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

def parse_tags(s: str) -> list[str]:
    s = (s or "").strip()
    if not s:
        return []
    return [x.strip() for x in s.split("|") if x.strip()]

# -----------------------------------------------------------
# Carregamento
# -----------------------------------------------------------
df = _safe_read_csv(CSV_PATH)
ctx = build_ctx()

if df is None:
    st.info("Índice `data/pdfs_index.csv` não encontrado. Mostrando todos os PDFs locais como fallback.")
    raws = list_all_local_pdfs()
    if not raws:
        st.warning("Nenhum PDF encontrado no repositório.")
        st.stop()
    # fallback simples (sem filtros por categoria/condição)
    for item in raws:
        if _HAS_PDF_VIEW:
            show_pdf(title=item["title"], local_path=item["path_local"], url=None, embed=False, key=item["title"])
        else:
            st.markdown(f"**{item['title']}**  \n`{item['path_local']}`")
    st.stop()

# normaliza colunas
df["category"] = df["category"].astype(str).fillna("")
df["tags"] = df["tags"].astype(str).fillna("")
df["condition"] = df["condition"].astype(str).fillna("")
df["path_local"] = df["path_local"].astype(str).fillna("")
df["url_remote"] = df["url_remote"].astype(str).fillna("")
df["title"] = df["title"].astype(str).fillna("Documento")

# -----------------------------------------------------------
# Filtros (sidebar)
# -----------------------------------------------------------
with st.sidebar:
    st.subheader("Filtros")
    categorias = sorted([c for c in df["category"].unique() if c])
    cat_sel = st.multiselect("Categoria", options=categorias, default=categorias)

    # tags possíveis (split por '|')
    all_tags = sorted(set(sum([parse_tags(t) for t in df["tags"]], [])))
    tag_sel = st.multiselect("Tags", options=all_tags, default=[])

    only_applicable = st.checkbox("Mostrar apenas aplicáveis ao paciente", value=False)
    try_embed = st.checkbox("Pré-visualizar via iframe (quando possível)", value=False)

# aplica filtros de categoria/tags
mask_cat = df["category"].isin(cat_sel) if cat_sel else df["category"].astype(bool)
mask_tag = df["tags"].apply(lambda s: True if not tag_sel else any(t in parse_tags(s) for t in tag_sel))

filtered = df[mask_cat & mask_tag].copy()

# aplica condição por paciente, se marcado
if only_applicable:
    filtered["__cond"] = filtered["condition"].apply(lambda e: eval_condition(e, ctx))
    filtered = filtered[filtered["__cond"] == True]  # noqa: E712

st.caption(f"Encontrados **{len(filtered)}** documentos.")

# -----------------------------------------------------------
# Busca textual
# -----------------------------------------------------------
q = st.text_input("Buscar por título…").strip().lower()
if q:
    filtered = filtered[filtered["title"].str.lower().str.contains(q)]

# -----------------------------------------------------------
# Renderização
# -----------------------------------------------------------
if filtered.empty:
    st.info("Nenhum documento com os filtros atuais.")
else:
    for _, row in filtered.iterrows():
        title = row["title"]
        local_path = row["path_local"] or ""
        remote = row["url_remote"] or ""
        cat = row["category"]
        tags = " | ".join(parse_tags(row["tags"]))

        st.markdown(f"#### {title}")
        meta = []
        if cat:
            meta.append(f"**Categoria:** {cat}")
        if tags:
            meta.append(f"**Tags:** {tags}")
        if meta:
            st.caption(" • ".join(meta))

        if _HAS_PDF_VIEW:
            show_pdf(
                title="",
                local_path=local_path if local_path else None,
                url=remote if remote else None,
                embed=try_embed,
                key=f"pdf_{row.get('id','')}"
            )
        else:
            # fallback simples
            cols = st.columns(2)
            if local_path and os.path.isfile(local_path):
                with open(local_path, "rb") as f:
                    pdf_bytes = f.read()
                cols[0].download_button(
                    "⬇️ Baixar PDF (local)", data=pdf_bytes,
                    file_name=os.path.basename(local_path),
                    mime="application/pdf", use_container_width=True
                )
            if remote:
                cols[1].link_button("🔗 Abrir PDF (online)", url=remote, use_container_width=True)
            if try_embed and (remote or local_path):
                st.components.v1.iframe(src=(remote or local_path), height=640)

        st.divider()
