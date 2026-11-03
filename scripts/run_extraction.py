import argparse
import json
import time
from pathlib import Path

from src.settings import Settings
from src.llm_client import LLMClient
from src.extractor import extract_cv

ap = argparse.ArgumentParser()
ap.add_argument("--target", choices=["hosted", "local"], required=True)
ap.add_argument("--version", default="v1")
ap.add_argument("--ids", nargs="*", default=None)
args = ap.parse_args()

if args.target == "hosted":
    client = LLMClient.from_settings(Settings())
else:
    client = LLMClient(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        models=["qwen3.5:2b"],
        timeout=600,
        max_retries=1,          # local slow, so adhigam
    )

EXTRA = {"reasoning_effort": "none"} if args.target == "local" else None
OUT = Path("outputs") / f"{args.target}_{args.version}"
OUT.mkdir(parents=True, exist_ok=True)

ids = args.ids or sorted(p.stem for p in Path("data/ground_truth").glob("cv_*.json"))

for cv_id in ids:
    text = Path(f"data/cvs/{cv_id}.txt").read_text(encoding="utf-8")
    try:
        res = extract_cv(client, text, version=args.version, extra_body=EXTRA)
        record = {
            "ok": res.ok, "repaired": res.repaired, "error": res.error,
            "model": res.model, "seconds": res.seconds,
            "prompt_tokens": res.prompt_tokens,
            "completion_tokens": res.completion_tokens,
            "first_error": res.first_error,
            "data": res.data.model_dump() if res.data else None,
        }
    except Exception as e:      # LLM call ae fail aana
        record = {"ok": False, "repaired": False, "error": str(e),
                  "model": None, "seconds": 0, "prompt_tokens": 0,
                  "completion_tokens": 0, "data": None}

    (OUT / f"{cv_id}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(cv_id, "ok" if record["ok"] else "FAIL",
          "repaired" if record["repaired"] else "", round(record["seconds"], 1), "s")
    time.sleep(8)               # free tier rate limit ku konjam gap
