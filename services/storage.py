# -*- coding: utf-8 -*-
"""
services/storage.py
Utilitários de leitura/gravação de arquivos do app (JSON, YAML, CSV) e
resolução de caminhos dentro da pasta `data/`.

Obs.:
- Não depende de Streamlit.
- Em ambientes como Streamlit Cloud, a escrita em disco pode não persistir
  entre sessões. Ainda assim, estas funções são úteis para ler os arquivos
  versionados no repositório (data/*.yaml, data/*.csv).
"""

from __future__ import annotations
import os
import io
import json
from typing import Any, Dict, Optional

# YAML e CSV são opcionais para manter leveza em ambientes restritos
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore


# ---------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------
DATA_DIR = os.path.join(os.getcwd(), "data")


def ensure_dir(path: str) -> None:
    """Garante que o diretório pai de `path` exista."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)


def in_data_dir(*parts: str) -> str:
    """Monta um caminho dentro da pasta `data/` (sem checar existência)."""
    return os.path.join(DATA_DIR, *parts)


def find_data_file(path_or_name: str) -> str:
    """
    Resolve um caminho para arquivo de dados aceitando:
    - caminho absoluto/relativo informado
    - nome simples que exista em `data/` (ex.: 'vaccines_rules.yaml')
    Retorna o caminho resolvido (pode não existir).
    """
    if os.path.isabs(path_or_name) or os.path.exists(path_or_name):
        return path_or_name
    candidate = in_data_dir(path_or_name)
    return candidate


# ---------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------
def load_json(path: str, default: Optional[Any] = None, encoding: str = "utf-8") -> Any:
    """Lê JSON; retorna `default` se arquivo não existir ou falhar."""
    p = find_data_file(path)
    try:
        with open(p, "r", encoding=encoding) as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path: str, obj: Any, encoding: str = "utf-8", indent: int = 2) -> bool:
    """Grava JSON; retorna True/False conforme sucesso."""
    try:
        ensure_dir(path)
        with open(path, "w", encoding=encoding) as f:
            json.dump(obj, f, ensure_ascii=False, indent=indent)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------
# YAML
# ---------------------------------------------------------------------
def load_yaml(path: str, default: Optional[Any] = None, encoding: str = "utf-8") -> Any:
    """Lê YAML com safe_load; retorna `default` se ausente/erro."""
    if yaml is None:
        return default
    p = find_data_file(path)
    try:
        with open(p, "r", encoding=encoding) as f:
            return yaml.safe_load(f)
    except Exception:
        return default


def save_yaml(path: str, obj: Any, encoding: str = "utf-8") -> bool:
    """Grava YAML (safe_dump); retorna True/False conforme sucesso."""
    if yaml is None:
        return False
    try:
        ensure_dir(path)
        with open(path, "w", encoding=encoding) as f:
            yaml.safe_dump(obj, f, allow_unicode=True, sort_keys=False)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------
def load_csv(path: str, encoding: str = "utf-8", dtype: Optional[Dict[str, Any]] = None):
    """
    Lê CSV usando pandas, se disponível.
    Retorna DataFrame ou None se pandas não estiver disponível ou houver erro.
    """
    if pd is None:
        return None
    p = find_data_file(path)
    try:
        return pd.read_csv(p, encoding=encoding, dtype=dtype)
    except Exception:
        return None


def save_csv(path: str, df, encoding: str = "utf-8") -> bool:
    """Grava DataFrame em CSV; retorna True/False. Requer pandas."""
    if pd is None:
        return False
    try:
        ensure_dir(path)
        df.to_csv(path, index=False, encoding=encoding)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------
# Bytes helpers (úteis para downloads)
# ---------------------------------------------------------------------
def bytes_from_text(text: str, encoding: str = "utf-8") -> bytes:
    """Converte texto em bytes para uso em botões de download."""
    return text.encode(encoding)


def bytes_from_json(obj: Any, encoding: str = "utf-8", indent: int = 2) -> bytes:
    """Serializa objeto JSON → bytes (UTF-8)."""
    s = json.dumps(obj, ensure_ascii=False, indent=indent)
    return s.encode(encoding)


def bytes_from_dataframe(df) -> bytes:
    """
    Serializa DataFrame em CSV (bytes). Retorna bytes vazios se pandas não estiver disponível.
    """
    if pd is None:
        return b""
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")

