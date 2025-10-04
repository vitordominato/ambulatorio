import streamlit as st
from schemas.patient import Patient
from datetime import date
import uuid

st.title("👤 Cadastro do Paciente")

with st.form("patient_form"):
    name = st.text_input("Nome completo")
    sex = st.selectbox("Sexo biológico", ["M", "F", "I"], index=2)
    birth = st.date_input("Data de nascimento", value=date(1980,1,1))
    comorb = st.multiselect(
        "Comorbidades",
        ["DM2","HAS","DPOC","Doença Renal","Doença Hepática","Cardiopatia","Neoplasia Ativa"]
    )
    smoking_packyears = st.number_input("Cargas tabágicas (pack-years)", min_value=0, step=1)
    is_health_worker = st.checkbox("Profissional de Saúde")
    is_pregnant = st.checkbox("Gestante")
    submitted = st.form_submit_button("Salvar/Atualizar")

if submitted:
    p = Patient(
        id=str(uuid.uuid4()),
        name=name,
        sex=sex,
        birth_date=str(birth),
        comorbidities=comorb,
        smoking_history_pack_years=int(smoking_packyears),
        is_health_worker=is_health_worker,
        is_pregnant=is_pregnant
    ).model_dump()
    st.session_state["patient"] = p
    st.success("Paciente salvo na sessão.")

if "patient" in st.session_state:
    st.subheader("Paciente atual")
    st.json(st.session_state["patient"])
else:
    st.info("Preencha e clique em **Salvar/Atualizar**.")

