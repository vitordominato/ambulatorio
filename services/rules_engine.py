from datetime import date
import operator

OPS = {
    ">=": operator.ge, "<=": operator.le, "==": operator.eq,
    ">": operator.gt, "<": operator.lt, "in": lambda a,b: a in b,
    "not_in": lambda a,b: a not in b
}

def age_in_years(birth_date: str) -> int:
    y,m,d = map(int, birth_date.split("-"))
    today = date.today()
    return today.year - y - ((today.month, today.day) < (m,d))

def _check(value, op, expected):
    if op == "range":
        lo, hi = expected
        return (value is not None) and (lo <= value <= hi)
    return OPS[op](value, expected)

def evaluate_rules(patient: dict, rules: list):
    """
    Cada regra: {field, op, value, reason}
    Retorna (True, [reasons...]) se todas forem satisfeitas.
    """
    reasons = []
    for r in rules:
        v = patient.get(r["field"])
        ok = _check(v, r["op"], r["value"])
        if not ok:
            return False, []
        if r.get("reason"): reasons.append(r["reason"])
    return True, reasons

