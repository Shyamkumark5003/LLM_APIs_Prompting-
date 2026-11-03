import json
import sys
from pathlib import Path

ids = sys.argv[1:]          # example: 01 02 03
for i in ids:
    cv_id = f"cv_{i}"
    print("=" * 60)
    print(Path(f"data/cvs/{cv_id}.txt").read_text(encoding="utf-8"))
    print("=" * 60)
    print(f"{cv_id}: CV paathu answer podu. Illaadhadhu na Enter mattum adi (null).")

    def ask(label):
        v = input(f"{label}: ").strip()
        return v or None

    name = ask("name")
    email = ask("email")
    phone = ask("phone")
    location = ask("location")
    skills_raw = ask("skills (comma vachu pirichu)")
    skills = [s.strip() for s in skills_raw.split(",")] if skills_raw else []
    education = ask("education")
    yrs = ask("total_years_experience (number)")

    gt = {
        "name": name, "email": email, "phone": phone, "location": location,
        "skills": skills, "education": education,
        "total_years_experience": float(yrs) if yrs else None,
    }
    Path(f"data/ground_truth/{cv_id}.json").write_text(
        json.dumps(gt, indent=2), encoding="utf-8")
    print("saved", cv_id, "\n")
