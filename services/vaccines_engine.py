import yaml
from services.rules_engine import evaluate_rules, age_in_years

def load_rules(path="data/vaccines_rules.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def suggest_vaccines(patient: dict, rules_dict: dict):
    p = {**patient, "age": age_in_years(patient["birth_date"])}
    out = []
    for key, item in rules_dict.items():
        ok, why = evaluate_rules(p, item["rules"])
        if ok:
            out.append({
                "vaccine": item["label"],
                "why": why,
                "schedule": item.get("schedule"),
                "refs": item.get("references", [])
            })
    return out

