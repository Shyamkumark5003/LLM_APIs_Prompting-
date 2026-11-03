import argparse
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--target", choices=["hosted", "local"], required=True)
ap.add_argument("--version", default="v1")
args = ap.parse_args()

FIELDS = ["name", "email", "phone", "location", "skills",
          "education", "total_years_experience"]


import re


def norm(v):
    if isinstance(v, str):
        v = re.sub(r"\([^)]*\)", "", v)   # bracket kulla text remove
    return " ".join(v.lower().split()) if isinstance(v, str) else v


def strict(field, gt, out):
    if field == "skills":
        return {norm(s) for s in (gt or [])} == {norm(s) for s in (out or [])}
    if field == "total_years_experience":
        if gt is None or out is None:
            return gt is None and out is None
        return abs(float(gt) - float(out)) <= 0.1
    return norm(gt) == norm(out)


def lenient(field, gt, out):
    """skills: F1 score (0 to 1). education: gt text model text kulla irukkaa."""
    if field == "skills":
        g = {norm(s) for s in (gt or [])}
        m = {norm(s) for s in (out or [])}
        if not g and not m:
            return 1.0
        hit = len(g & m)
        if hit == 0:
            return 0.0
        p, r = hit / len(m), hit / len(g)
        return 2 * p * r / (p + r)
    if field == "education":
        if gt is None or out is None:
            return float(gt is None and out is None)
        return float(norm(gt) in norm(out) or norm(out) in norm(gt))
    return float(strict(field, gt, out))


S = {f: 0.0 for f in FIELDS}
L = {f: 0.0 for f in FIELDS}
n = fails = repaired = 0
secs = []

for gt_path in sorted(Path("data/ground_truth").glob("cv_*.json")):
    out_path = Path("outputs") / f"{args.target}_{args.version}" / gt_path.name
    if not out_path.exists():
        continue
    gt = json.loads(gt_path.read_text())
    rec = json.loads(out_path.read_text())
    n += 1
    secs.append(rec["seconds"])
    repaired += rec["repaired"]
    if not rec["ok"]:
        fails += 1
        continue
    for f in FIELDS:
        S[f] += strict(f, gt.get(f), rec["data"].get(f))
        L[f] += lenient(f, gt.get(f), rec["data"].get(f))

print(f"\nTarget: {args.target} | CVs: {n}")
print(f"  {'field':25s} {'strict':>8s} {'lenient':>8s}")
for f in FIELDS:
    print(f"  {f:25s} {S[f]:>5.0f}/{n}  {L[f]:>5.1f}/{n}")
tot = n * len(FIELDS)
print(f"\nStrict accuracy  : {sum(S.values()):.0f}/{tot} = {100*sum(S.values())/tot:.1f}%")
print(f"Lenient accuracy : {sum(L.values()):.1f}/{tot} = {100*sum(L.values())/tot:.1f}%")
print(f"Avg time         : {sum(secs)/len(secs):.1f} s")
print(f"Failures         : {fails}")
print(f"Repair needed    : {repaired}")
