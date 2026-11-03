import logging
from src.settings import Settings
from src.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)

messages = [{"role": "user", "content": "Say hi in one short sentence."}]

# 1. Hosted (.env la irundhu)
hosted = LLMClient.from_settings(Settings())
print("HOSTED:", hosted.chat(messages))

# 2. Local Ollama (same class, base_url mattum veru)
local = LLMClient(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    models=["qwen3.5:2b"],
    timeout=120,
)
print("LOCAL:", local.chat(messages))
