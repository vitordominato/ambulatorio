import streamlit as st, yaml
from services.rules_engine import evaluate_rules, age_in_years

st.title("🔍 Recomendações de Rastreamento")
patient = st.session_state.get("patient")

if not patient:
    st.warning("Cadastre um paciente primeiro.")
    st.stop()

rules = yaml.safe_load(open("data/screening_rules.yaml","r",encoding="utf-8"))
patient = {**patient, "age": age_in_years(patient["birth_date"])}

if st.button("Gerar recomendações"):
    hits = []
    for key, item in rules.items():
        ok, why = evaluate_rules(patient, item["rules"])
        if ok:
            hits.append((item["label"], item.get("guidance",""), item.get("link_pdf",""), why))
    if not hits:
        st.info("Nenhuma recomendação com os dados atuais.")
    else:
        for label, guide, link, why in hits:
            with st.container(border=True):
                st.markdown(f"**{label}**")
                if guide: st.write(guide)
                if link: st.markdown(f"[Ver diretriz (PDF)]({link})")
                if why: st.caption("Motivos: " + "; ".join(why))

