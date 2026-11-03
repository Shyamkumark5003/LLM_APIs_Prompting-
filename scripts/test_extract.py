from pathlib import Path
from src.settings import Settings
from src.llm_client import LLMClient
from src.extractor import extract_cv

client = LLMClient.from_settings(Settings())
text = Path("data/cvs/sample.txt").read_text()
res = extract_cv(client, text)

print("OK:", res.ok, "| repaired:", res.repaired, "| sec:", round(res.seconds, 2))
print(res.data.model_dump_json(indent=2) if res.data else res.error)
