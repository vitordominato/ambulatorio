import streamlit as st
from services.trials_service import load_trials, eligible_trials
from services.rules_engine import age_in_years

st.title("🧪 Pesquisas Clínicas – Elegibilidade")
patient = st.session_state.get("patient")

if not patient:
    st.warning("Cadastre um paciente primeiro.")
    st.stop()

patient = {**patient, "age": age_in_years(patient["birth_date"])}
trials = load_trials("data/trials.yaml")
matches = eligible_trials(patient, trials)

st.write(f"Encontradas **{len(matches)}** possibilidades.")
for t in matches:
    with st.container(border=True):
        st.markdown(f"**{t['title']}**")
        st.write(f"Status: {t['status']}")
        if t.get("contacts"): st.write("Contatos:", ", ".join(t["contacts"]))
        if t.get("links"):
            for link in t["links"]: st.markdown(f"- {link}")
        st.caption("Motivos do match: " + "; ".join(t["match_reasons"]))

