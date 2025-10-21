# -*- coding: utf-8 -*-
# components/reco_card.py

from __future__ import annotations
from typing import Any, Dict, Iterable, Optional, Union
import streamlit as st

def _md_list(items: Union[str, Iterable[str]]) -> str:
    if items is None:
        return ""
    if isinstance(items, str):
        return f"- {items}"
    return "\n".join(f"- {x}" for x in items if str(x).strip())

def show_reco_card(
    card: Dict[str, Any],
    *,
    key_prefix: str = "reco",
    show_divider: bool = True,
    compact: bool = False,
) -> None:
    """
    Mostra um cartão de recomendação clínica/vacinal.

    Espera um dict com chaves opcionais:
      title: str
      subtitle: str
      rationale: str | list[str]
      action: str | list[str]       (conduta)
      notes: str | list[str]
      references: str | list[str]
      badge: str                    (ex.: "Classe I • Nível A", "USPSTF A", etc.)

    Exemplo mínimo:
      show_reco_card({
          "title": "Vacina Influenza",
          "rationale": "Idade ≥ 60 anos",
          "action": "Aplicar dose anual",
          "references": ["SBIm 2024", "MS 2024"]
      })
    """
    title = card.get("title", "Recomendação")
    subtitle = card.get("subtitle")
    rationale = card.get("rationale")
    action = card.get("action")
    notes = card.get("notes")
    refs = card.get("references")
    badge = card.get("badge")

    with st.container(border=True):
        # Cabeçalho
        cols = st.columns([1, 1]) if badge else [None]
        if badge:
            with cols[0]:
                st.markdown(f"### {title}")
                if subtitle:
                    st.caption(subtitle)
            with cols[1]:
                st.markdown(
                    f"<div style='text-align:right;'>"
                    f"<span style='padding:6px 10px;border-radius:12px;"
                    f"background:#EEF6FF;border:1px solid #CFE2FF;'>"
                    f"{badge}"
                    f"</span></div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(f"### {title}")
            if subtitle:
                st.caption(subtitle)

        # Corpo
        if rationale:
            st.markdown("**Racional:**")
            st.markdown(_md_list(rationale))

        if action:
            st.markdown("**Conduta:**")
            st.markdown(_md_list(action))

        if notes:
            lab = "Observação" if isinstance(notes, str) else "Observações"
            st.markdown(f"**{lab}:**")
            st.markdown(_md_list(notes))

        if refs:
            with st.expander("📚 Referências"):
                st.markdown(_md_list(refs))

    if show_divider and not compact:
        st.divider()
