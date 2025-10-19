# pages/3_💉_Vacinas.py
import streamlit as st
from uuid import uuid4
from schemas.patient import Patient
from services.rules_engine import RulesEngine, render_recommendation
from components.reco_card import show_reco_card

st.set_page_config(page_title="Vacinas", page_icon="💉", layout="wide")
st.title("Assistente de Rastreamento e Vacinação")

# ------------------ Formulário (resumo) ------------------
sexo_label = st.selectbox("Sexo biológico", ["Masculino", "Feminino"])
sexo = "M" if sexo_label == "Masculino" else "F"
idade = st.number_input("Idade", min_value=0, max_value=120, value=30, step=1)
prof_saude = st.checkbox("Profissional de Saúde")

st.subheader("🧍 Histórico Patológico Pregresso (HPP)")
c1, c2 = st.columns(2)
with c1:
    imc_ge_25 = st.checkbox("IMC ≥ 25")
    gestante = st.checkbox("Gestante") if sexo == "F" else False
    dm = st.checkbox("Diabetes Mellitus")
    imunossuprimido = st.checkbox("Imunossuprimido")
    renal = st.checkbox("Doença renal crônica")
    neoplasia = st.checkbox("Neoplasia ativa")
    har = st.checkbox("Hipertensão arterial resistente (≥3 drogas)")
    dm_hba1c = st.checkbox("Diabetes (HbA1c > 7,5%)")
    alcool = st.checkbox("Alcoolismo")
with c2:
    tabagista = st.checkbox("Tabagista ou ex-tabagista")
    dpoc = st.checkbox("DPOC")
    cardio = st.checkbox("Doença cardiovascular crônica")
    hepatica = st.checkbox("Doença hepática crônica")
    enxaq = st.checkbox("Cefaleia tipo migranosa refratária")
    ldl190 = st.checkbox("Dislipidemia (LDL ≥ 190 mg/dL)")
    colageno = st.checkbox("Doenças do colágeno/tecido conectivo")
    uso_aco = st.checkbox("Uso de contraceptivo oral")
    txp = st.checkbox("Paciente transplantado (qualquer órgão)")

st.subheader("👨‍👩‍👧‍👦 Histórico Familiar (HF)")
c3, c4 = st.columns(2)
with c3:
    hf_prostata = st.checkbox("Histórico familiar de câncer de próstata")
    hf_coronaria = st.checkbox("Hist. familiar de doença coronariana")
    hf_avc = st.checkbox("Hist. familiar de AVC isquêmico")
    hf_aaa = st.checkbox("Hist. familiar de AAA")
with c4:
    hf_mama = st.checkbox("Histórico familiar de câncer de mama")
    hf_colorretal = st.checkbox("Histórico familiar de câncer colorretal")
    hf_ateromatose = st.checkbox("Hist. familiar de ateromatose sistêmica")
    hf_an_intra = st.checkbox("Hist. familiar de aneurisma intracraniano")
    hf_outro_an = st.checkbox("Outro aneurisma arterial conhecido (fam.)")

# ------------------ Construção do Patient ------------------
paciente = Patient(
    id=str(uuid4()), sex=sexo, age=idade, is_health_worker=prof_saude,
    imc_ge_25=imc_ge_25, smoker_or_ex=tabagista, is_pregnant=gestante,
    dm=dm, dpoc=dpoc, imunossuprimido=imunossuprimido, cardiovascular_cronica=cardio,
    renal_cronica=renal, hepatica_cronica=hepatica, neoplasia_ativa=neoplasia,
    hipertensao_resistente=har, dm_hba1c_maior_75=dm_hba1c, alcoolismo=alcool,
    enxaqueca_refrataria=enxaq, ldl_maior_190=ldl190, doencas_colageno=colageno,
    uso_aco=uso_aco, transplantado=txp,
    famhx_mama=hf_mama, famhx_prostata=hf_prostata, famhx_colorretal=hf_colorretal,
    famhx_coronariana=hf_coronaria, famhx_avc_isquemico=hf_avc, famhx_aaa=hf_aaa,
    famhx_ateromatose=hf_ateromatose, famhx_an_intracraniano=hf_an_intra, famhx_outro_aneurisma=hf_outro_an,
)

# ------------------ Engine ------------------
engine = RulesEngine()
out = engine.evaluate(paciente)

# ------------------ Render ------------------
if out.recommendations:
    st.success("Plano sugerido (ordenado por prioridade). O primeiro card é o ponto de partida.")
    for i, rec in enumerate(out.recommendations):
        card = render_recommendation(rec, highlight=(i == 0))
        show_reco_card(card)
else:
    st.info(out.no_recommendation_message or "Sem recomendações específicas no momento.")
