# services/medicos_parser.py
from io import BytesIO
from typing import List, Dict
import re
import yaml
import pandas as pd
from docx import Document

DIAS = ["segunda", "terça", "terca", "quarta", "quinta", "sexta", "sábado", "sabado"]

def _is_dia_line(text: str) -> bool:
    t = text.lower().strip()
    return t.startswith("dias de atendimento:") or any(d in t for d in DIAS)

def parse_docx_bytes(docx_bytes: bytes) -> List[Dict]:
    """
    Lê o .docx e retorna uma lista de registros:
    [{especialidade, medico, dias:[...]}, ...]
    Regras:
    - Uma linha 'Especialidade' (em maiúsculas, sem ':'), seguida por pares:
      <nome do médico>   /   'Dias de atendimento: ...'
    - Ignora realces/cores do DOCX (o texto puro importa).
    - Linhas vazias são puladas.
    """
    doc = Document(BytesIO(docx_bytes))
    records = []
    current_spec = None
    pending_name = None

    # regex para identificar linha que parece especialidade (tudo maiúsculo com letras/acentos e espaços)
    re_spec = re.compile(r"^[A-ZÁÉÍÓÚÂÊÎÔÛÃÕÇ ]{3,}$")
    re_dias = re.compile(r"(?i)dias de atendimento:\s*(.*)")

    for p in doc.paragraphs:
        text = (p.text or "").strip()
        if not text:
            continue

        # especialidade?
        if re_spec.match(text) and "DIAS DE ATENDIMENTO" not in text:
            current_spec = text.title().strip()
            pending_name = None
            continue

        # linha de dias?
        m = re_dias.match(text)
        if m and current_spec and pending_name:
            dias_str = m.group(1).strip() or ""
            # normaliza separadores
            dias = [x.strip().capitalize() for x in re.split(r"[;,/]| e ", dias_str) if x.strip()]
            records.append({"especialidade": current_spec, "medico": pending_name, "dias": dias})
            pending_name = None
            continue

        # se não é especialidade nem 'dias', e temos uma especialidade ativa → é nome de médico
        if current_spec and not _is_dia_line(text):
            pending_name = text.strip()

    # fallback: se sobrou nome sem “dias”, registra ao menos vazio
    if current_spec and pending_name:
        records.append({"especialidade": current_spec, "medico": pending_name, "dias": []})

    return records

def to_yaml_by_specialty(records: List[Dict]) -> str:
    out = {}
    for r in records:
        out.setdefault(r["especialidade"], []).append({"nome": r["medico"], "dias": r["dias"]})
    return yaml.safe_dump(out, allow_unicode=True, sort_keys=True)

def to_csv(records: List[Dict]) -> str:
    df = pd.DataFrame(records)
    df["dias"] = df["dias"].apply(lambda x: ", ".join(x))
    return df.to_csv(index=False)

