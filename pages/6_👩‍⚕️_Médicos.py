import streamlit as st
import requests
from services.medicos_parser import parse_docx_bytes, to_yaml_by_specialty, to_csv
import pandas as pd
import io

st.title("👩‍⚕️ Médicos por Especialidade")

st.markdown("""
Carrega a lista de médicos a partir do **arquivo DOCX** e organiza por especialidade e dias de atendimento.
Você pode:
1) Ler direto do GitHub (URL raw do `.docx`), ou  
2) Fazer **upload** de um arquivo `.docx` atualizado.  
Depois, baixe **YAML** e/ou **CSV** para salvar em `data_medicos/` do seu repositório.
""")

# 1) Fonte do DOCX
col1, col2 = st.columns([3,2])
with col1:
    default_url = "https://raw.githubusercontent.com/vitordominato/ambulatorio/main/M%C3%A9dicos.ambulatório.CHN.docx"
    docx_url = st.text_input("URL raw do DOCX no GitHub", value=default_url)
with col2:
    uploaded = st.file_uploader("Ou faça upload do DOCX", type=["docx"])

bytes_data = None
if uploaded is not None:
    bytes_data = uploaded.read()
elif docx_url:
    try:
        r = requests.get(docx_url, timeout=30)
        r.raise_for_status()
        bytes_data = r.content
    except Exception as e:
        st.error(f"Erro ao baixar o DOCX: {e}")

if not bytes_data:
    st.info("Informe a URL ou faça upload do arquivo para continuar.")
    st.stop()

# 2) Parsing
try:
    records = parse_docx_bytes(bytes_data)
except Exception as e:
    st.error(f"Erro ao processar o DOCX: {e}")
    st.stop()

st.success(f"Extraídos **{len(records)}** registros (médico × especialidade).")

# 3) Filtros e tabela
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

# 4) Exports (YAML/CSV)
yaml_text = to_yaml_by_specialty(records)
csv_text = to_csv(records)

st.download_button("⬇️ Baixar YAML (por especialidade)",
                   data=yaml_text.encode("utf-8"),
                   file_name="especialidades_medicos.yaml",
                   mime="text/yaml")

st.download_button("⬇️ Baixar CSV (tabela completa)",
                   data=csv_text.encode("utf-8"),
                   file_name="especialidades_medicos.csv",
                   mime="text/csv")

st.caption("Salve o(s) arquivo(s) baixado(s) em `data_medicos/` no GitHub para versionar.")

