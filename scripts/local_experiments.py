import hashlib
import json
import sys
import urllib.request
from pathlib import Path

from src.extractor import _wrap_cv
from src.prompts import load_prompt

URL = "http://localhost:11434/api/chat"
MODEL = "qwen3.5:2b"
SYSTEM = load_prompt("cv_extract_v4")


def call(user_text, **options):
    body = {
        "model": MODEL, "stream": False, "think": False,
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": user_text}],
        "options": {"num_predict": 700, **options},
    }
    req = urllib.request.Request(URL, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1200) as r:
        return json.load(r)


def summary(d):
    text = d["message"]["content"]
    h = hashlib.md5(text.encode()).hexdigest()[:8]
    try:
        j = json.loads(text)
        info = f"name={j.get('name')!r} skills={len(j.get('skills') or [])} years={j.get('total_years_experience')}"
    except Exception:
        info = "NOT VALID JSON"
    return h, info, d.get("prompt_eval_count"), d.get("eval_count")


mode = sys.argv[1]

if mode == "sampling":
    cv = _wrap_cv(Path("data/cvs/cv_05.txt").read_text(encoding="utf-8"))
    runs = [("temp 0", {"temperature": 0})] * 3 \
         + [("temp 1.5", {"temperature": 1.5})] * 3 \
         + [("temp 1.5 + seed 42", {"temperature": 1.5, "seed": 42})] * 2
    for label, opts in runs:
        h, info, pe, ec = summary(call(cv, **opts))
        print(f"{label:22s} hash={h}  {info}  tokens_out={ec}", flush=True)

elif mode == "ctx":
    base = Path("data/cvs/cv_05.txt").read_text(encoding="utf-8")
    filler = ("Hobbies and interests: reading novels, hiking on weekends, "
              "photography, cooking regional dishes, and volunteering at local events. ") * 250
    long_doc = _wrap_cv(base + "\n\n" + filler + "\n\nEducation: B.Tech, Marker University")
    print("document chars:", len(long_doc), "(approx tokens:", len(long_doc) // 4, ")")
    for label, opts in [("default ctx", {"temperature": 0}),
                        ("num_ctx 8192", {"temperature": 0, "num_ctx": 8192})]:
        h, info, pe, ec = summary(call(long_doc, **opts))
        print(f"{label:14s} prompt_tokens_seen={pe}  {info}  hash={h}", flush=True)
