import yaml
from services.rules_engine import evaluate_rules

def load_rules(path="data/vaccines_rules.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def suggest_vaccines(patient: dict, rules: dict):
    recs = []
    for key, vax in rules.items():
        ok, reasons = evaluate_rules(patient, vax["rules"])
        if ok:
            recs.append({
                "vaccine": vax["label"],
                "schedule": vax.get("schedule", ""),
                "refs": vax.get("refs", []),
                "why": reasons,
                "contraindications": vax.get("contraindications", []),
            })
    return recs

