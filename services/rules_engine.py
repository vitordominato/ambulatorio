def _eval_single(patient, rule):
    field = rule["field"]; op = rule["op"]; value = rule["value"]
    reason = rule.get("reason", "")
    if field not in patient: return False, None
    val = patient[field]
    ok = {
        "==":  val == value,
        "!=":  val != value,
        ">=":  val >= value,
        "<=":  val <= value,
        ">":   val >  value,
        "<":   val <  value,
        "in":  val in value,
        "range": value[0] <= val <= value[1],
    }.get(op, False)
    return ok, (reason if ok and reason else None)

def evaluate_rules(patient, rules):
    """
    Regras aceitas:
      - lista simples (AND): [ {field, op, value}, ... ]
      - any_of: pelo menos um dos blocos passa (OR)
        any_of:
          - [ {..}, {..} ]        # bloco-1 (AND interno)
          - [ {..} ]              # bloco-2
    Retorna (passou, [motivos])
    """
    reasons = []

    # caso 'any_of'
    if isinstance(rules, dict) and "any_of" in rules:
        for block in rules["any_of"]:
            block_ok = True; block_reasons = []
            for r in block:
                ok, why = _eval_single(patient, r)
                if not ok:
                    block_ok = False; break
                if why: block_reasons.append(why)
            if block_ok:
                reasons.extend(block_reasons)
                return True, reasons
        return False, []

    # lista simples (AND)
    passed = True
    for r in rules:
        ok, why = _eval_single(patient, r)
        if not ok: passed = False
        elif why: reasons.append(why)
    return passed, reasons
