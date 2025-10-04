import streamlit as st
from services.vaccines_engine import suggest_vaccines, load_rules, age_in_years

st.title("💉 Recomendações Vacinais (SBIm)")
patient = st.session_state.get("patient")

if not patient:
    st.warning("Cadastre um paciente primeiro.")
    st.stop()

rules = load_rules("data/vaccines_rules.yaml")
patient = {**patient, "age": age_in_years(patient["birth_date"])}

sugs = suggest_vaccines(patient, rules)
if not sugs:
    st.success("Sem pendências vacinais.")
else:
    for s in sugs:
        with st.container(border=True):
            st.markdown(f"**{s['vaccine']}** — recomendado")
            if s.get("schedule"): st.write("Esquema:", s["schedule"])
            if s.get("why"): st.caption("Motivos: " + "; ".join(s["why"]))
            if s.get("refs"):
                with st.expander("Referências"):
                    for r in s["refs"]:
                        st.markdown(f"- {r}")

