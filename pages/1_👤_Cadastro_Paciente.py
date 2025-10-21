import streamlit as st

st.markdown("### 🩺 Fatores clínicos e antecedentes")

# cria duas colunas bem equilibradas
col_esq, col_dir = st.columns(2)

with col_esq:
    imc_ge_25 = st.checkbox("IMC ≥ 25", value=st.session_state["patient"].get("imc_ge_25", False))
    gestante = st.checkbox("Gestante", value=st.session_state["patient"].get("is_pregnant", False))
    famhx_prostata = st.checkbox("Histórico familiar de câncer de próstata", value=st.session_state["patient"].get("famhx_prostata", False))
    famhx_mama = st.checkbox("Histórico familiar de câncer de mama", value=st.session_state["patient"].get("famhx_mama", False))
    famhx_colorretal = st.checkbox("Histórico familiar de câncer colorretal", value=st.session_state["patient"].get("famhx_colorretal", False))
    dm = st.checkbox("Diabetes Mellitus", value=st.session_state["patient"].get("dm", False))
    imunossuprimido = st.checkbox("Imunossuprimido", value=st.session_state["patient"].get("imunossuprimido", False))
    dpoc = st.checkbox("DPOC", value=st.session_state["patient"].get("dpoc", False))
    renal = st.checkbox("Doença renal crônica", value=st.session_state["patient"].get("renal_cronica", False))
    hepatica = st.checkbox("Doença hepática crônica", value=st.session_state["patient"].get("hepatica_cronica", False))
    neoplasia = st.checkbox("Neoplasia ativa", value=st.session_state["patient"].get("neoplasia_ativa", False))
    alcoolismo = st.checkbox("Alcoolismo", value=False)
    transplante = st.checkbox("Paciente transplantado (qualquer órgão)", value=False)

with col_dir:
    tabagismo = st.checkbox("Tabagista ou ex-tabagista", value=st.session_state["patient"].get("smoker_or_ex", False))
    cardiovascular = st.checkbox("Doença cardiovascular crônica", value=st.session_state["patient"].get("cardiovascular_cronica", False))
    dislipidemia = st.checkbox("Dislipidemia (LDL > 190 mg/dL)", value=False)
    hipertensao = st.checkbox("Hipertensão arterial resistente (≥3 drogas)", value=False)
    migranea = st.checkbox("Cefaleia tipo migrânea refratária", value=False)
    colageno = st.checkbox("Doenças do colágeno / tecido conectivo", value=False)
    contraceptivo = st.checkbox("Uso de contraceptivo oral", value=False)
    hist_coronaria = st.checkbox("Histórico familiar de doença coronariana", value=False)
    hist_ateromatose = st.checkbox("Histórico familiar de ateromatose sistêmica", value=False)
    hist_avc = st.checkbox("Histórico familiar de AVC isquêmico", value=False)
    hist_aaa = st.checkbox("Histórico familiar de aneurisma de aorta abdominal (AAA)", value=False)
    hist_intracr = st.checkbox("Histórico familiar de aneurisma intracraniano", value=False)
    outro_aneurisma = st.checkbox("Outro aneurisma arterial conhecido", value=False)

# botão de salvar
if st.button("💾 Salvar/Atualizar", use_container_width=True):
    st.session_state["patient"].update({
        "imc_ge_25": imc_ge_25,
        "is_pregnant": gestante,
        "famhx_prostata": famhx_prostata,
        "famhx_mama": famhx_mama,
        "famhx_colorretal": famhx_colorretal,
        "dm": dm,
        "imunossuprimido": imunossuprimido,
        "dpoc": dpoc,
        "renal_cronica": renal,
        "hepatica_cronica": hepatica,
        "neoplasia_ativa": neoplasia,
        "smoker_or_ex": tabagismo,
        "cardiovascular_cronica": cardiovascular,
    })
    st.success("Dados atualizados com sucesso!")
