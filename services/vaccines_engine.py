import yaml
from services.rules_engine import evaluate_rules

def load_rules(path="data/vaccines_rules.yaml"):
    """Carrega as regras de vacinação do arquivo YAML."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def suggest_vaccines(patient: dict, rules: dict):
    """Avalia todas as regras e retorna as vacinas recomendadas."""
    recs = []
    for key, vax in rules.items():
        ok, reasons = evaluate_rules(patient, vax["rules"])
        if ok:
            recs.append({
                "vaccine": vax["label"],
                "schedule": vax.get("schedule", ""),
                "refs": vax.get("refs", []),
                "why": reasons
            })
    return recs
