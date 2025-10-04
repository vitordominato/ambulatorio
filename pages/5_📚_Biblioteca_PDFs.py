import os, glob
import streamlit as st
import urllib.parse
import requests

st.title("📚 Biblioteca de Guias e Protocolos (GitHub)")

OWNER = "vitordominato"
REPO  = "ambulatorio"
BRANCH = "main"

RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}"

@st.cache_data(ttl=300, show_spinner=False)
def list_pdfs_locally():
    # Varre o repositório clonado pelo Streamlit (sem usar API do GitHub)
    files = sorted(glob.glob("**/*.pdf", recursive=True))
    items = []
    for p in files:
        # ignora possíveis pastas de cache/venv
        if any(x in p.split(os.sep) for x in [".venv", "venv", ".git"]):
            continue
        url = f"{RAW_BASE}/{urllib.parse.quote(p)}"
        items.append({"title": os.path.basename(p), "path": p, "url": url})
    return items

def list_pdfs_via_api(path=""):
    # Fallback: usa API do GitHub, com token se presente em st.secrets
    headers = {}
    token = st.secrets.get("GITHUB_TOKEN", None)
    if token:
        headers["Authorization"] = f"token {token}"

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}"
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    out = []
    for it in r.json():
        if it["type"] == "file" and it["name"].lower().endswith(".pdf"):
            out.append({"title": it["name"], "path": it["path"], "url": it["download_url"]})
        elif it["type"] == "dir":
            out.extend(list_pdfs_via_api(it["path"]))
    return out

# 1) Tenta listar localmente (sem limite de rate)
pdfs = list_pdfs_locally()

# 2) Se nada encontrado (situação rara), tenta API (com token se houver)
if not pdfs:
    try:
        pdfs = list_pdfs_via_api("")
    except Exception as e:
        st.error(f"Não foi possível listar PDFs: {e}")
        st.caption("Sugestão: defina um GITHUB_TOKEN em st.secrets ou use a varredura local do repo.")
        st.stop()

if not pdfs:
    st.info("Nenhum PDF encontrado no repositório.")
    st.stop()

# Busca e seleção
q = st.text_input("Buscar por nome do arquivo...")
data = [p for p in pdfs if (q.lower() in p["title"].lower())] if q else pdfs
st.write(f"Encontrados **{len(data)}** documentos.")
options = [f'{p["title"]} — ({p["path"]})' for p in data]
sel = st.selectbox("Abrir documento", ["Selecione..."] + options)

if sel != "Selecione...":
    idx = options.index(sel) - 1
    url = data[idx]["url"]
    st.download_button("Baixar PDF", url, type="primary")
    st.markdown(
        f'<iframe src="{url}" width="100%" height="720" style="border:none;"></iframe>',
        unsafe_allow_html=True
    )

