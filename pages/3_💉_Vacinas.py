import streamlit as st
from services.vaccines_engine import suggest_vaccines, load_rules

st.title("💉 Recomendações Vacinais (SBIm)")
patient = st.session_state.get("patient")

if not patient:
    st.warning("Cadastre um paciente primeiro.")
    st.stop()

rules = load_rules("data/vaccines_rules.yaml")

# Agora a idade já está no dicionário patient
vaccines = suggest_vaccines(patient, rules)

if not vaccines:
    st.success("Sem pendências vacinais detectadas.")
else:
    for v in vaccines:
        with st.container(border=True):
            st.markdown(f"**{v['vaccine']}** — recomendado")
            if v.get("schedule"):
                st.write("Esquema:", v["schedule"])
            if v.get("why"):
                st.caption("Motivos: " + "; ".join(v["why"]))
            if v.get("refs"):
                with st.expander("Referências"):
                    for r in v["refs"]:
                        st.markdown(f"- {r}")
