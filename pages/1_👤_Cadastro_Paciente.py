# -*- coding: utf-8 -*-
# pages/1_🧑‍⚕️_Cadastro_Paciente.py

import streamlit as st

st.header("Cadastro do Paciente")

# --------------------------------------------------------------------------------------
# Utilitários de estado
# --------------------------------------------------------------------------------------
def _ensure_patient_state():
    """Garante que st.session_state['patient'] exista e esteja saneado (sexo M/F apenas)."""
    patient = st.session_state.get("patient", {})

    sex = patient.get("sex", "M")
    if sex not in ("M", "F"):  # retrocompatibilidade: remove qualquer valor antigo (ex.: "I")
        sex = "M"

    def _b(x):  # força bool
        return bool(patient.get(x, False))

    st.session_state["patient"] = {
        "id": patient.get("id", ""),
        "sex": sex,
        "age": int(patient.get("age", 0)) if str(patient.get("age", "")).isdigit() else 0,
        "is_health_worker": _b("is_health_worker"),

        # fatores/antecedentes padronizados
        "imc_ge_25": _b("imc_ge_25"),
        "is_pregnant": _b("is_pregnant"),
        "famhx_prostata": _b("famhx_prostata"),
        "famhx_mama": _b("famhx_mama"),
        "famhx_colorretal": _b("famhx_colorretal"),
        "dm": _b("dm"),
        "imunossuprimido": _b("imunossuprimido"),
        "dpoc": _b("dpoc"),
        "renal_cronica": _b("renal_cronica"),
        "hepatica_cronica": _b("hepatica_cronica"),
        "neoplasia_ativa": _b("neoplasia_ativa"),
        "smoker_or_ex": _b("smoker_or_ex"),
        "cardiovascular_cronica": _b("cardiovascular_cronica"),

        # fatores adicionais exibidos nesta página (não usados em regras agora)
        "hipertensao_resistente": _b("hipertensao_resistente"),
        "migranea_refrataria": _b("migranea_refrataria"),
        "colageno_tecido": _b("colageno_tecido"),
        "contraceptivo_oral": _b("contraceptivo_oral"),
        "hist_coronaria": _b("hist_coronaria"),
        "hist_ateromatose": _b("hist_ateromatose"),
        "hist_avc_isquemico": _b("hist_avc_isquemico"),
        "hist_aaa": _b("hist_aaa"),
        "hist_intracr": _b("hist_intracr"),
        "outro_aneurisma": _b("outro_aneurisma"),
        "dislipidemia_ldl190": _b("dislipidemia_ldl190"),

        "notes": patient.get("notes", ""),
    }


_ensure_patient_state()
p = st.session_state["patient"]

# --------------------------------------------------------------------------------------
# Formulário de cadastro
# --------------------------------------------------------------------------------------
with st.form("cadastro_paciente"):
    st.subheader("Dados básicos")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        pid = st.text_input("Identificador (opcional)", value=p.get("id", ""), key="pid_input")
    with c2:
        # Selectbox com apenas M/F, com rótulos amigáveis
        labels_sexo = {"M": "Masculino", "F": "Feminino"}
        opcoes_sexo = list(labels_sexo.keys())
        idx = opcoes_sexo.index(p.get("sex", "M")) if p.get("sex", "M") in opcoes_sexo else 0
        sexo = st.selectbox(
            "Sexo biológico",
            options=opcoes_sexo,
            index=idx,
            format_func=lambda v: labels_sexo[v],
            key="sexo_select",
        )
    with c3:
        idade = st.number_input("Idade", min_value=0, max_value=120, value=int(p.get("age", 0)), step=1)

    prof_saude = st.checkbox("Profissional de Saúde", value=p.get("is_health_worker", False))

    st.markdown("### 🧾 Fatores clínicos e antecedentes")

    col_esq, col_dir = st.columns(2)

    # -------------------- COLUNA ESQUERDA --------------------
    with col_esq:
        imc_ge_25 = st.checkbox("IMC ≥ 25", value=p.get("imc_ge_25", False))
        gestante = st.checkbox("Gestante", value=p.get("is_pregnant", False))
        famhx_prostata = st.checkbox(
            "Histórico familiar de câncer de próstata", value=p.get("famhx_prostata", False)
        )
        famhx_mama = st.checkbox(
            "Histórico familiar de câncer de mama", value=p.get("famhx_mama", False)
        )
        famhx_colorretal = st.checkbox(
            "Histórico familiar de câncer colorretal", value=p.get("famhx_colorretal", False)
        )
        dm = st.checkbox("Diabetes Mellitus", value=p.get("dm", False))
        imunossuprimido = st.checkbox("Imunossuprimido", value=p.get("imunossuprimido", False))
        dpoc = st.checkbox("DPOC", value=p.get("dpoc", False))
        renal = st.checkbox("Doença renal crônica", value=p.get("renal_cronica", False))
        hepatica = st.checkbox("Doença hepática crônica", value=p.get("hepatica_cronica", False))
        neoplasia = st.checkbox("Neoplasia ativa", value=p.get("neoplasia_ativa", False))

    # -------------------- COLUNA DIREITA --------------------
    with col_dir:
        tabagismo = st.checkbox(
            "Tabagista ou ex-tabagista", value=p.get("smoker_or_ex", False)
        )
        cardiovascular = st.checkbox(
            "Doença cardiovascular crônica", value=p.get("cardiovascular_cronica", False)
        )
        dislipidemia = st.checkbox(
            "Dislipidemia (LDL > 190 mg/dL)", value=p.get("dislipidemia_ldl190", False)
        )
        hipertensao = st.checkbox(
            "Hipertensão arterial resistente (≥ 3 drogas)", value=p.get("hipertensao_resistente", False)
        )
        migranea = st.checkbox(
            "Cefaleia tipo migrânea refratária", value=p.get("migranea_refrataria", False)
        )
        colageno = st.checkbox(
            "Doenças do colágeno/tecido conectivo", value=p.get("colageno_tecido", False)
        )
        contraceptivo = st.checkbox(
            "Uso de contraceptivo oral", value=p.get("contraceptivo_oral", False)
        )
        hist_coronaria = st.checkbox(
            "Histórico familiar de doença coronariana", value=p.get("hist_coronaria", False)
        )
        hist_ateromatose = st.checkbox(
            "Histórico familiar de ateromatose sistêmica", value=p.get("hist_ateromatose", False)
        )
        hist_avc = st.checkbox(
            "Histórico familiar de AVC isquêmico", value=p.get("hist_avc_isquemico", False)
        )
        hist_aaa = st.checkbox(
            "Histórico familiar de aneurisma de aorta abdominal (AAA)", value=p.get("hist_aaa", False)
        )
        hist_intracr = st.checkbox(
            "Histórico familiar de aneurisma intracraniano", value=p.get("hist_intracr", False)
        )
        outro_aneurisma = st.checkbox(
            "Outro aneurisma arterial conhecido", value=p.get("outro_aneurisma", False)
        )

    # Observações livres (opcional)
    notes = st.text_area("Observações (opcional)", value=p.get("notes", ""), height=100)

    enviar = st.form_submit_button("💾 Salvar/Atualizar", use_container_width=True)

# --------------------------------------------------------------------------------------
# Persistência ao salvar
# --------------------------------------------------------------------------------------
if enviar:
    st.session_state["patient"].update({
        "id": st.session_state.get("pid_input", "").strip(),
        "sex": st.session_state.get("sexo_select", "M"),
        "age": int(idade),
        "is_health_worker": bool(prof_saude),

        "imc_ge_25": bool(imc_ge_25),
        "is_pregnant": bool(gestante),
        "famhx_prostata": bool(famhx_prostata),
        "famhx_mama": bool(famhx_mama),
        "famhx_colorretal": bool(famhx_colorretal),
        "dm": bool(dm),
        "imunossuprimido": bool(imunossuprimido),
        "dpoc": bool(dpoc),
        "renal_cronica": bool(renal),
        "hepatica_cronica": bool(hepatica),
        "neoplasia_ativa": bool(neoplasia),
        "smoker_or_ex": bool(tabagismo),
        "cardiovascular_cronica": bool(cardiovascular),

        "dislipidemia_ldl190": bool(dislipidemia),
        "hipertensao_resistente": bool(hipertensao),
        "migranea_refrataria": bool(migranea),
        "colageno_tecido": bool(colageno),
        "contraceptivo_oral": bool(contraceptivo),
        "hist_coronaria": bool(hist_coronaria),
        "hist_ateromatose": bool(hist_ateromatose),
        "hist_avc_isquemico": bool(hist_avc),
        "hist_aaa": bool(hist_aaa),
        "hist_intracr": bool(hist_intracr),
        "outro_aneurisma": bool(outro_aneurisma),

        "notes": notes,
    })

    # sanity check final do sexo
    if st.session_state["patient"]["sex"] not in ("M", "F"):
        st.session_state["patient"]["sex"] = "M"

    st.success("Dados do paciente salvos/atualizados com sucesso!")

# --------------------------------------------------------------------------------------
# Resumo rápido (para conferência)
# --------------------------------------------------------------------------------------
with st.expander("Ver resumo salvo"):
    st.json(st.session_state["patient"])
