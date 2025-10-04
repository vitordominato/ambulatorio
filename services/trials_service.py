import yaml
from services.rules_engine import evaluate_rules

def load_trials(path="data/trials.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []

def eligible_trials(patient: dict, trials: list):
    out = []
    for t in trials:
        ok_in, why_in = evaluate_rules(patient, t.get("include_rules", []))
        ok_ex, _      = evaluate_rules(patient, t.get("exclude_rules", []))
        if ok_in and not ok_ex:
            out.append({**t, "match_reasons": why_in})
    return out

