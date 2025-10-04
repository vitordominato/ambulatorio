import streamlit as st, pandas as pd
from components.pdf_viewer import show_pdf

st.title("📚 Biblioteca de Guias e Protocolos")
df = pd.read_csv("data/pdfs_index.csv")

cat = st.selectbox("Categoria", ["Todos"] + sorted(df["category"].dropna().unique().tolist()))
q = st.text_input("Buscar título...")

f = df.copy()
if cat != "Todos": f = f[f["category"] == cat]
if q: f = f[f["title"].str.contains(q, case=False, na=False)]

st.dataframe(f[["title","category"]], use_container_width=True, hide_index=True)
sel = st.selectbox("Abrir documento", ["Selecione..."] + f["title"].tolist())
if sel != "Selecione...":
    url = f.loc[f["title"]==sel, "url"].iloc[0]
    st.download_button("Baixar PDF", url)
    show_pdf(url)

