import streamlit as st, requests

st.title("📚 Biblioteca de Guias e Protocolos (GitHub)")

OWNER = "vitordominato"      # ajuste se mudar
REPO  = "ambulatorio"        # ajuste se mudar
BRANCH = "main"

@st.cache_data(show_spinner=False, ttl=300)
def list_repo_pdfs(path=""):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    items = []
    for it in r.json():
        if it["type"] == "file" and it["name"].lower().endswith(".pdf"):
            raw = it["download_url"]  # link direto
            items.append({"title": it["name"], "path": it["path"], "url": raw})
        elif it["type"] == "dir":
            items.extend(list_repo_pdfs(it["path"]))  # recursivo
    return items

try:
    pdfs = list_repo_pdfs("")
    if not pdfs:
        st.info("Nenhum PDF encontrado no repositório.")
    else:
        q = st.text_input("Buscar por nome do arquivo...")
        data = [p for p in pdfs if (q.lower() in p["title"].lower())] if q else pdfs
        st.write(f"Encontrados **{len(data)}** documentos.")
        options = [f'{p["title"]} — ({p["path"]})' for p in data]
        sel = st.selectbox("Abrir documento", ["Selecione..."] + options)
        if sel != "Selecione...":
            idx = options.index(sel) - 1
            url = data[idx]["url"]
            st.download_button("Baixar PDF", url)
            st.markdown(f"""
                <iframe src="{url}" width="100%" height="720" style="border:none;"></iframe>
            """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Erro ao listar PDFs do GitHub: {e}")
    st.caption("Verifique o nome do repositório/branch ou tente novamente.")

