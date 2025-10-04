import operator

OPS = {
    ">=": operator.ge, "<=": operator.le, "==": operator.eq,
    ">": operator.gt, "<": operator.lt, "in": lambda a,b: a in b,
    "not_in": lambda a,b: a not in b
}

def _check_simple(value, op, expected):
    if op == "range":
        lo, hi = expected
        return (value is not None) and (lo <= value <= hi)
    return OPS[op](value, expected)

def _check_count_true(patient: dict, fields: list, op: str, value: int):
    # conta quantos campos estão True; compara com value via op (>=, >, ==, etc.)
    count = sum(1 for f in fields if bool(patient.get(f, False)))
    return OPS[op](count, value), count

def evaluate_rules(patient: dict, rules: list):
    """
    Cada regra pode ser:
      - simples: {field, op, value, reason}
      - contagem: {fields: [...], op: \">=\", value: 3, reason: \"≥3 fatores\"}
    Todas as regras na lista precisam ser verdadeiras (AND).
    """
    reasons = []
    for r in rules:
        if "fields" in r:
            ok, count = _check_count_true(patient, r["fields"], r["op"], r["value"])
            if not ok:
                return False, []
            if r.get("reason"):
                reasons.append(f'{r["reason"]} (n={count})')
        else:
            v = patient.get(r["field"])
            ok = _check_simple(v, r["op"], r["value"])
            if not ok:
                return False, []
            if r.get("reason"):
                reasons.append(r["reason"])
    return True, reasons
