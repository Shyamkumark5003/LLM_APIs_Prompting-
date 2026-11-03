import sys

from src.llm_client import LLMClient
from src.vision import extract_invoice

KEY = {"vendor": "Brightline Supplies Pvt Ltd", "invoice_number": "INV-2026-0417",
       "invoice_date": "12 Oct 2026", "bill_to": "Kavya Traders", "total": 11750.0}

client = LLMClient(base_url="http://localhost:11434/v1", api_key="ollama",
                   models=["qwen3.5:2b"], timeout=900, max_retries=1)

for path in sys.argv[1:]:
    print("=" * 60, path, flush=True)
    try:
        data, r, note = extract_invoice(client, path,
                                        extra_body={"reasoning_effort": "none"})
    except Exception as e:
        print("ERROR:", type(e).__name__, e)
        continue
    print(f"time {r.seconds:.0f}s | tokens in {r.prompt_tokens} out {r.completion_tokens}")
    if data is None:
        print(note)
        print("raw:", r.text[:300])
        continue
    if note:
        print(note)
    got = data.model_dump()
    ok = 0
    for k, v in KEY.items():
        match = (abs(got[k] - v) < 0.01) if k == "total" and got[k] is not None else got[k] == v
        ok += match
        print(f"  {k:15s} {'OK ' if match else 'BAD'}  key={v!r}  model={got[k]!r}")
    print(f"  fields correct: {ok}/{len(KEY)}")
