# services/rules_engine.py
from typing import Any, Dict, List, Tuple, Union

Number = Union[int, float]

def _to_number(x: Any) -> Tuple[bool, Number]:
    try:
        if isinstance(x, bool):
            return False, x  # não converter bool
        if isinstance(x, (int, float)):
            return True, x
        if isinstance(x, str):
            # troca vírgula por ponto se vier "50,0"
            x = x.replace(",", ".").strip()
            return True, float(x) if ("." in x or "e" in x.lower()) else int(x)
    except Exception:
        pass
    return False, x

def _is_collection(x: Any) -> bool:
    return isinstance(x, (list, tuple, set))

def _eval_single(patient: Dict[str, Any], rule: Dict[str, Any]) -> Tuple[bool, str]:
    field = rule.get("field")
    op = rule.get("op")
    value = rule.get("value")
    reason = rule.get("reason", "")

    if field not in patient:
        return False, ""

    val = patient[field]

    # Conversões numéricas quando possível
    v_is_num, v_num = _to_number(val)
    w_is_num, w_num = _to_number(value)

    ok = False

    if op == "==":
        ok = (val == value)
    elif op == "!=":
        ok = (val != value)
    elif op in {">", ">=", "<", "<="}:
        # só compara numericamente se os dois forem números
        if v_is_num and w_is_num:
            if op == ">":  ok = v_num >  w_num
            if op == ">=": ok = v_num >= w_num
            if op == "<":  ok = v_num <  w_num
            if op == "<=": ok = v_num <= w_num
        else:
            ok = False
    elif op == "in":
        # só faz membership se value for coleção; senão cai para igualdade
        if _is_collection(value):
            ok = (val in value)
        else:
            ok = (val == value)
    elif op == "range":
        # espera lista/tupla com 2 elementos numéricos
        if _is_collection(value) and len(value) == 2:
            a_ok, a = _to_number(value[0])
            b_ok, b = _to_number(value[1])
            if v_is_num and a_ok and b_ok:
                lo, hi = (a, b) if a <= b else (b, a)
                ok = (lo <= v_num <= hi)
            else:
                ok = False
        else:
            ok = False
    else:
        ok = False

    return (ok, reason if ok and reason else "")

def evaluate_rules(patient: Dict[str, Any], rules: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Regras aceitas:
      - Lista simples (AND): [ {field, op, value, reason?}, ... ]
      - any_of (OR por blocos):
        rules:
          any_of:
            - [ {..}, {..} ]   # Bloco 1 (AND interno)
            - [ {..} ]         # Bloco 2
    Retorna: (passou, [motivos])
    """
    reasons: List[str] = []

    # OU por blocos
    if isinstance(rules, dict) and "any_of" in rules:
        for block in rules["any_of"]:
            block_ok = True
            block_reasons: List[str] = []
            for r in block:
                ok, why = _eval_single(patient, r)
                if not ok:
                    block_ok = False
                    break
                if why:
                    block_reasons.append(why)
            if block_ok:
                reasons.extend(block_reasons)
                return True, reasons
        return False, []

    # AND simples
    passed = True
    for r in rules:
        ok, why = _eval_single(patient, r)
        if not ok:
            passed = False
        elif why:
            reasons.append(why)

    return passed, reasons

