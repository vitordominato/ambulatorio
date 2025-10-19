# components/reco_card.py
import streamlit as st

def show_reco_card(card: dict):
    st.markdown(f"### {card['title']}")
    st.write(card["rationale"])
    st.markdown(f"**Conduta:**\n\n{card['action']}")
    if card["notes"]:
        st.markdown(f"**Observações:**\n\n{card['notes']}")
    if card["references"]:
        with st.expander("📎 Referências"):
            st.markdown(card["references"])
    st.divider()
