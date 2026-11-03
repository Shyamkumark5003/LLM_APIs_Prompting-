import json
import sys
from pathlib import Path

target = sys.argv[1]
for gt_path in sorted(Path("data/ground_truth").glob("cv_*.json")):
    out = json.loads((Path("outputs") / target / gt_path.name).read_text())
    gt = json.loads(gt_path.read_text())
    print("=" * 50, gt_path.stem)
    if not out["ok"]:
        print("FAIL:", out["error"])
        continue
    d = out["data"]
    for f in ["education", "total_years_experience", "name"]:
        print(f"{f}\n   YOU  : {gt.get(f)}\n   MODEL: {d.get(f)}")
    g = {s.lower() for s in gt["skills"]}
    m = {s.lower() for s in d["skills"]}
    print("skills missing in model:", sorted(g - m))
    print("skills extra in model  :", sorted(m - g))
