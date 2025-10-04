# services/medicos_parser.py
from io import BytesIO
from typing import List, Dict
import re
import yaml
import pandas as pd
from docx import Document

def parse_docx_bytes(docx_bytes: bytes) -> List[Dict]:
    """
    Faz a leitura completa de um arquivo DOCX e extrai especialidade, médico e dias.
    Compatível com formatações diversas do documento do CHN.
    """
    doc = Document(BytesIO(docx_bytes))
    records = []
    current_spec = None
    current_name = None

    # regex para especialidades (em maiúsculas com acentos)
    re_spec = re.compile(r"^[A-ZÁÉÍÓÚÂÊÎÔÛÃÕÇ ]{3,}$")
    # regex para dias (aceita qualquer combinação de palavras com 'dia' ou 'atendimento')
    re_dias = re.compile(r"(?i)(dia|atendimento|segunda|terça|terca|quarta|quinta|sexta|sábado|sabado)")

    for p in doc.paragraphs:
        text = (p.text or "").strip()
        if not text:
            continue

        # identifica especialidade
        if re_spec.match(text) and not text.lower().startswith("dias"):
            current_spec = text.title().strip()
            continue

        # identifica “Dias de atendimento” (ou variações)
        if re_dias.search(text) and "atendimento" in text.lower():
            if current_spec and current_name:
                dias_raw = text.split(":")[-1].strip()
                dias = [d.strip().capitalize() for d in re.split(r"[,;/]| e ", dias_raw) if d.strip()]
                records.append({
                    "especialidade": current_spec,
                    "medico": current_name,
                    "dias": dias if dias else []
                })
                current_name = None
            continue

        # caso contrário, é o nome do médico
        if current_spec:
            current_name = text.strip()

    # fallback: se sobrou nome sem “dias”
    if current_spec and current_name:
        records.append({
            "especialidade": current_spec,
            "medico": current_name,
            "dias": []
        })

    return records

def to_yaml_by_specialty(records: List[Dict]) -> str:
    out = {}
    for r in records:
        out.setdefault(r["especialidade"], []).append({"nome": r["medico"], "dias": r["dias"]})
    return yaml.safe_dump(out, allow_unicode=True, sort_keys=True)

def to_csv(records: List[Dict]) -> str:
    if not records:
        return ""
    df = pd.DataFrame(records)
    if "dias" not in df.columns:
        df["dias"] = [[] for _ in range(len(df))]
    df["dias"] = df["dias"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
    return df.to_csv(index=False)

