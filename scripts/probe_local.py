from pathlib import Path
from src.llm_client import LLMClient
from src.prompts import load_prompt
from src.extractor import _wrap_cv

client = LLMClient(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    models=["qwen3.5:2b"],
    timeout=600,
    max_retries=1,
)
text = Path("data/cvs/cv_05.txt").read_text(encoding="utf-8")
messages = [
    {"role": "system", "content": load_prompt("cv_extract_v1")},
    {"role": "user", "content": _wrap_cv(text)},
]
r = client.chat(messages, extra_body={"reasoning_effort": "none"})
print("seconds:", round(r.seconds, 1))
print("prompt_tokens:", r.prompt_tokens, "| completion_tokens:", r.completion_tokens)
print("tokens/sec:", round(r.completion_tokens / r.seconds, 1))
print(r.text[:500])
