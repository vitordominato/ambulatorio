# -*- coding: utf-8 -*-
import os
import streamlit as st

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Assistente Clínico",
    page_icon="🩺",
    layout="wide",
)

# =========================
# ESTADO GLOBAL / SESSION
# =========================
def _init_globals():
    # Configs globais simples e reutilizáveis pelo app
    st.session_state.setdefault("APP_CONFIG", {
        # pasta local de PDFs no repositório raiz
        "pdf_folder": ".",  # raiz do repo (onde estão os PDFs já enviados)
        # exemplo de URLs remotas (se usar GitHub raw futuramente)
        "pdf_remote_base": "",  # ex.: "https://raw.githubusercontent.com/vitordominato/ambulatorio/main"
    })

    # Sinalizadores de módulos opcionais (não devem derrubar o app)
    if "MODULES" not in st.session_state:
        st.session_state["MODULES"] = {
            "reco_card": False,
            "trials_service": False,
        }

    # Health-check leve dos módulos opcionais (sem crashar)
    try:
        from components import reco_card  # noqa: F401
        st.session_state["MODULES"]["reco_card"] = True
    except Exception:
        st.session_state["MODULES"]["reco_card"] = False

    try:
        from services import trials_service  # noqa: F401
        st.session_state["MODULES"]["trials_service"] = True
    except Exception:
        st.session_state["MODULES"]["trials_service"] = False

    # Estado do paciente padronizado (sexo apenas M/F)
    # Se algum valor antigo (ex.: "I") estiver salvo, saneamos para "M"
    patient = st.session_state.get("patient", {})
    sex = patient.get("sex", "M")
    if sex not in ("M", "F"):
        sex = "M"
    st.session_state["patient"] = {
        # campos essenciais (pode ser expandido nas páginas)
        "id": patient.get("id", ""),
        "sex": sex,           # <- somente "M" ou "F"
        "age": int(patient.get("age", 0)) if str(patient.get("age", "")).isdigit() else 0,

        # fatores/antecedentes usados no restante do app
        "imc_ge_25": bool(patient.get("imc_ge_25", False)),
        "smoker_or_ex": bool(patient.get("smoker_or_ex", False)),
        "is_pregnant": bool(patient.get("is_pregnant", False)),
        "famhx_mama": bool(patient.get("famhx_mama", False)),
        "famhx_prostata": bool(patient.get("famhx_prostata", False)),
        "famhx_colorretal": bool(patient.get("famhx_colorretal", False)),
        "dm": bool(patient.get("dm", False)),
        "dpoc": bool(patient.get("dpoc", False)),
        "imunossuprimido": bool(patient.get("imunossuprimido", False)),
        "cardiovascular_cronica": bool(patient.get("cardiovascular_cronica", False)),
        "renal_cronica": bool(patient.get("renal_cronica", False)),
        "hepatica_cronica": bool(patient.get("hepatica_cronica", False)),
        "neoplasia_ativa": bool(patient.get("neoplasia_ativa", False)),
        "notes": patient.get("notes", ""),
    }

_init_globals()

# =========================
# UI – HOME
# =========================
with st.sidebar:
    st.markdown("### app")
    st.caption("Use o menu lateral (acima) para navegar entre as páginas do aplicativo.")

st.title("🩺 Assistente de Rastreamento, Vacinação e Pesquisas")

st.markdown(
    """
Bem-vindo! Use o menu **Pages** (canto superior esquerdo, ícone de páginas) para navegar:
- **Cadastro do Paciente** – preencha/edite dados básicos e fatores clínicos.
- **Rastreamento** – recomendações de exames conforme perfil.
- **Vacinas** – sugestões com base nas diretrizes (SBIm) e condições do paciente.
- **Pesquisas Clínicas** – (em desenvolvimento) visualização de elegibilidade.
- **Biblioteca de PDFs** – acesso a diretrizes e guias salvos no repositório.
"""
)

# Cartões de status rápidos
mod = st.session_state["MODULES"]
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Módulo de Reco de Vacinas", "Ativo" if mod["reco_card"] else "Indisponível")
    if not mod["reco_card"]:
        st.caption("A aba **Vacinas** continuará carregando com mensagem informativa (sem erro).")

with col2:
    st.metric("Módulo de Pesquisas Clínicas", "Ativo" if mod["trials_service"] else "Indisponível")
    if not mod["trials_service"]:
        st.caption("A aba **Pesquisas Clínicas** também está blindada até reativarmos o serviço.")

with col3:
    p = st.session_state["patient"]
    st.metric("Sexo (M/F apenas)", p["sex"])
    st.caption("Qualquer valor fora de M/F é automaticamente saneado para **M**.")

st.divider()

# Resumo do estado do paciente (visual rápido; edição é feita na página de cadastro)
with st.expander("Ver estado atual do paciente (resumo)"):
    p = st.session_state["patient"]
    st.json({
        "id": p["id"],
        "sex": p["sex"],
        "age": p["age"],
        "fatores": {
            k: v for k, v in p.items()
            if k in [
                "imc_ge_25", "smoker_or_ex", "is_pregnant",
                "famhx_mama", "famhx_prostata", "famhx_colorretal",
                "dm", "dpoc", "imunossuprimido",
                "cardiovascular_cronica", "renal_cronica",
                "hepatica_cronica", "neoplasia_ativa"
            ]
        }
    })

st.info("Dica: mantenha esta aba aberta. As outras páginas usam os dados salvos em memória.")
