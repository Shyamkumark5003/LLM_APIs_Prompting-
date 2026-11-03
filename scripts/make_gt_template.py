import json
from pathlib import Path

GT = Path("data/ground_truth")
GT.mkdir(parents=True, exist_ok=True)

IDS = [1, 2, 3, 4, 5, 6, 7, 8, 19, 20]

template = {
    "name": "",
    "email": None,
    "phone": None,
    "location": None,
    "skills": [],
    "education": None,
    "total_years_experience": None,
}

for i in IDS:
    p = GT / f"cv_{i:02d}.json"
    if not p.exists():
        p.write_text(json.dumps(template, indent=2), encoding="utf-8")
        print("created", p)
    else:
        print("skip (already exists)", p)
