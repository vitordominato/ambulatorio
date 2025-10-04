import streamlit as st
from schemas.patient import Patient
import uuid, yaml

st.title("👤 Cadastro do Paciente")

# carrega fatores do YAML
FACTS = yaml.safe_load(open("data/factors.yaml","r",encoding="utf-8"))["fatores"]

with st.form("patient_form"):
    sex = st.selectbox("Sexo biológico", ["M", "F", "I"], index=2)
    age = st.number_input("Idade", min_value=0, max_value=120, step=1)
    is_health_worker = st.checkbox("Profissional de Saúde")

    st.markdown("### 📋 Fatores clínicos e antecedentes")
    col1, col2 = st.columns(2)
    checks = {}
    for i, item in enumerate(FACTS):
        col = col1 if i % 2 == 0 else col2
        with col:
            checks[item["key"]] = st.checkbox(item["label"])

    submitted = st.form_submit_button("Salvar/Atualizar")

if submitted:
    payload = {
        "id": str(uuid.uuid4()),
        "sex": sex,
        "age": int(age),
        "comorbidities": [],
        "is_health_worker": is_health_worker,

        # mapeamentos 1:1 com factors.yaml
        "imc_ge_25": checks.get("imc_ge_25", False),
        "smoker_or_ex": checks.get("smoker_or_ex", False),
        "is_pregnant": checks.get("gestante", False),
        "famhx_mama": checks.get("famhx_mama", False),
        "famhx_prostata": checks.get("famhx_prostata", False),
        "famhx_colorretal": checks.get("famhx_colorretal", False),
        "dm": checks.get("dm", False),
        "dpoc": checks.get("dpoc", False),
        "imunossuprimido": checks.get("imunossuprimido", False),
        "cardiovascular_cronica": checks.get("cardiovascular_cronica", False),
        "renal_cronica": checks.get("renal_cronica", False),
        "hepatica_cronica": checks.get("hepatica_cronica", False),
        "neoplasia_ativa": checks.get("neoplasia_ativa", False),

        # neurovascular (se você estiver usando)
        "enxaqueca_refrataria": checks.get("enxaqueca_refrataria", False),
        "hipertensao_resistente": checks.get("hipertensao_resistente", False),
        "dislipidemia_ldl_maior_190": checks.get("dislipidemia_ldl_maior_190", False),
        "hbA1c_maior_7_5": checks.get("hbA1c_maior_7_5", False),
        "doencas_colageno": checks.get("doencas_colageno", False),
        "alcoolismo": checks.get("alcoolismo", False),
        "uso_aco": checks.get("uso_aco", False),
        "histfam_coronariana": checks.get("histfam_coronariana", False),
        "histfam_ateromatose_sist": checks.get("histfam_ateromatose_sist", False),
        "histfam_avc_isquemico": checks.get("histfam_avc_isquemico", False),
        "histfam_aneurisma_intracraniano": checks.get("histfam_aneurisma_intracraniano", False),

        # AAA/aneurismas
        "histfam_aaa": checks.get("histfam_aaa", False),
        "outro_aneurisma": checks.get("outro_aneurisma", False),
        "transplantado": checks.get("transplantado", False),
    }
    p = Patient(**payload).model_dump()
    st.session_state["patient"] = p
    st.success("Paciente salvo na sessão.")

if "patient" in st.session_state:
    st.subheader("Paciente atual")
    st.json(st.session_state["patient"])
else:
    st.info("Preencha e clique em **Salvar/Atualizar**.")

