"""Demonstração OPSPECTA: 100 ordens de serviço inteiramente sintéticas.
Python 3.10+, apenas biblioteca padrão. Nenhum dado real.
"""
import csv
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

SEED, N = 20261109, 100
random.seed(SEED)
BASE = datetime(2026, 1, 1, 8, 0)
ASSETS = [f"SYN-{i:03d}" for i in range(1, 21)]
CATEGORIES = ["power", "communication", "sensor", "software", "configuration"]
REQUIRED = ("order_id", "asset_id", "opened_at", "closed_at", "category", "action")
records = []
for i in range(N):
    asset = ASSETS[random.randrange(len(ASSETS))]
    opened = BASE + timedelta(days=random.randrange(90), hours=random.randrange(10))
    duration = random.choice([2, 4, 8, 12, 24, 48, 72])
    category = random.choice(CATEGORIES)
    action = random.choice(["inspection", "reset", "component_review", "configuration_review"])
    row = {
        "order_id": f"OS-SYN-{i + 1:04d}", "asset_id": asset,
        "opened_at": opened.isoformat(timespec="minutes"),
        "closed_at": (opened + timedelta(hours=duration)).isoformat(timespec="minutes"),
        "category": category, "action": action,
    }
    if i % 13 == 0:
        row["action"] = ""
    records.append(row)

out = Path(__file__).with_name("os_sinteticas.csv")
with out.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=REQUIRED)
    writer.writeheader()
    writer.writerows(records)

missing = sum(not str(r["action"]).strip() for r in records)
by_asset = defaultdict(list)
for row in records:
    by_asset[row["asset_id"]].append(row)

recurrences = []
for asset, rows in by_asset.items():
    rows.sort(key=lambda r: r["opened_at"])
    for previous, current in zip(rows, rows[1:]):
        hours = (datetime.fromisoformat(current["opened_at"]) - datetime.fromisoformat(previous["opened_at"])).total_seconds() / 3600
        if 0 <= hours <= 30 * 24 and previous["category"] == current["category"]:
            recurrences.append((asset, previous["order_id"], current["order_id"]))

durations = [(datetime.fromisoformat(r["closed_at"]) - datetime.fromisoformat(r["opened_at"])).total_seconds() / 3600 for r in records]
print(f"Registros sintéticos: {len(records)}")
print(f"Campo 'action' ausente: {missing} ({100 * missing/N:.1f}%)")
print(f"Duração média registrada (h): {sum(durations)/N:.1f}")
print(f"Pares candidatos a reincidência: {len(recurrences)}")
print(f"Categorias: {dict(sorted(Counter(r['category'] for r in records).items()))}")
print(f"CSV gerado: {out}")
