# -*- coding: utf-8 -*-
# components/pdf_viewer.py

from __future__ import annotations
import os
import streamlit as st

def show_pdf(
    *,
    title: str = "Documento (PDF)",
    local_path: str | None = None,
    url: str | None = None,
    embed: bool = False,
    height: int = 640,
    key: str | None = None,
) -> None:
    """
    Viewer simples de PDF com download local e/ou link externo.
    - Se `local_path` existir, exibe botão de download.
    - Se `url` existir, exibe botão/link para abrir online.
    - `embed=True` tenta incorporar via iframe (pode falhar em alguns deploys).

    Uso:
      show_pdf(title="Protocolo X", local_path="assets/protocolos/x.pdf", url="https://.../x.pdf")
    """
    with st.container(border=True):
        st.markdown(f"#### {title}")

        has_local = bool(local_path) and os.path.isfile(local_path)
        has_remote = bool(url)

        c1, c2 = st.columns(2)

        if has_local:
            with open(local_path, "rb") as f:
                pdf_bytes = f.read()
            c1.download_button(
                "⬇️ Baixar PDF",
                data=pdf_bytes,
                file_name=os.path.basename(local_path),
                mime="application/pdf",
                use_container_width=True,
                key=(key or "") + "_dl",
            )

        if has_remote:
            c2.link_button("🔗 Abrir PDF (online)", url=url, use_container_width=True, key=(key or "") + "_lnk")

        if not has_local and not has_remote:
            st.warning("PDF não encontrado. Informe `local_path` existente ou `url` pública do arquivo.")

        if embed and (has_remote or has_local):
            st.divider()
            st.caption("Pré-visualização (iframe)")
            src = url if has_remote else local_path
            # Nota: iframe de caminho local pode não funcionar em cloud/Streamlit Community.
            st.components.v1.iframe(src=src, height=height)
