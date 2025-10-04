import streamlit as st
import requests
from services.medicos_parser import parse_docx_bytes, to_yaml_by_specialty, to_csv
import pandas as pd

st.title("👩‍⚕️ Médicos por Especialidade")

st.markdown("""
Carrega a lista de médicos a partir do **arquivo DOCX** e organiza por especialidade e dias de atendimento.

- Ler direto do GitHub (URL *raw* do `.docx`), **ou**
- Fazer **upload** de um arquivo `.docx` atualizado.
Depois, baixe **YAML** e/ou **CSV** para salvar em `data_medicos/`.
""")

# ⚠️ URL COM ACENTOS PRECISA SER 100% ESCAPADA
default_url = (
    "https://raw.githubusercontent.com/vitordominato/ambulatorio/main/"
    "M%C3%A9dicos.ambulat%C3%B3rio.CHN.docx"
)

col1, col2 = st.columns([3,2])
with col1:
    docx_url = st.text_input("URL raw do DOCX no GitHub", value=default_url)
with col2:
    uploaded = st.file_uploader("Ou faça upload do DOCX", type=["docx"])

bytes_data = None
source = None

if uploaded is not None:
    bytes_data = uploaded.read()
    source = "upload"
elif docx_url:
    try:
        r = requests.get(docx_url, timeout=30)
        r.raise_for_status()
        bytes_data = r.content
        source = "url"
    except Exception as e:
        st.error(f"Erro ao baixar o DOCX: {e}")

if not bytes_data:
    st.info("Informe a URL (corrigida) ou faça upload do arquivo.")
    st.stop()

# Parse
try:
    records = parse_docx_bytes(bytes_data)
except Exception as e:
    st.error(f"Erro ao processar o DOCX: {e}")
    st.stop()

st.success(f"Extraídos **{len(records)}** registros (médico × especialidade).")

# Debug se ficar em 0
with st.expander("Diagnóstico (se extraiu 0)"):
    st.write(f"Fonte: {source}")
    st.write("Se ainda estiver 0, tente **upload** do DOCX direto aqui (pode haver problema na URL com acentos).")

# Tabela e filtros
especialidades = sorted({r["especialidade"] for r in records})
dias_set = sorted({d for r in records for d in r["dias"]})
colf1, colf2, colf3 = st.columns(3)
with colf1:
    spec_sel = st.selectbox("Filtrar por especialidade", ["Todas"] + especialidades)
with colf2:
    dia_sel = st.selectbox("Filtrar por dia", ["Todos"] + dias_set)
with colf3:
    q = st.text_input("Buscar por nome do médico")

f = records
if spec_sel != "Todas":
    f = [r for r in f if r["especialidade"] == spec_sel]
if dia_sel != "Todos":
    f = [r for r in f if dia_sel in r["dias"]]
if q:
    f = [r for r in f if q.lower() in r["medico"].lower()]

df = pd.DataFrame(f)
if not df.empty:
    df["dias"] = df["dias"].apply(lambda x: ", ".join(x))

st.dataframe(df, use_container_width=True, hide_index=True)

# Downloads
yaml_text = to_yaml_by_specialty(records)
csv_text = to_csv(records)
st.download_button("⬇️ Baixar YAML (por especialidade)", yaml_text.encode("utf-8"),
                   file_name="especialidades_medicos.yaml", mime="text/yaml")
st.download_button("⬇️ Baixar CSV (tabela completa)", csv_text.encode("utf-8"),
                   file_name="especialidades_medicos.csv", mime="text/csv")

