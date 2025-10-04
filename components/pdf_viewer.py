import streamlit as st

def show_pdf(url: str, height: int = 720):
    st.markdown(f"""
        <iframe src="{url}" width="100%" height="{height}" style="border:none;"></iframe>
    """, unsafe_allow_html=True)

