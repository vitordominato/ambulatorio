# -*- coding: utf-8 -*-
# components/pdf_viewer.py
import streamlit as st


def show_pdf(title: str = "", path_local: str = "", url: str = "", key: str | None = None):
    """
    Exibe informações e links para um PDF (local ou remoto).
    - title: título do documento
    - path_local: caminho local para download
    - url: link remoto (ex: GitHub RAW)
    - key: string única (opcional)
    """
    key = str(key or f"pdf_{title.replace(' ', '_')}")
    st.markdown(f"### {title}")

    if url:
        # Garante chave única (string)
        safe_key = str(key).replace(" ", "_")
        st.link_button("🔗 Abrir PDF (online)", url=url, use_container_width=True, key=safe_key + "_lnk")

    if path_local:
        try:
            with open(path_local, "rb") as f:
                st.download_button(
                    label="💾 Baixar PDF",
                    data=f,
                    file_name=path_local.split("/")[-1],
                    mime="application/pdf",
                    key=key + "_dl",
                    use_container_width=True,
                )
        except FileNotFoundError:
            st.warning("Arquivo local não encontrado.")
