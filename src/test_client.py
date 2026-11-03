import logging
from src.settings import Settings
from src.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)

messages = [{"role": "user", "content": "Say hi in one short sentence."}]

# 1. Hosted (settings la irundhu)
hosted = LLMClient.from_settings(Settings())
r = hosted.chat(messages)
print("HOSTED:", r)

# 2. Local Ollama (same class, base_url mattum veru)
local = LLMClient(
    base_url="http://localhost:11434/v1",
    api_key="ollama",            # Ollama ku edhavadhu ezhuthu podhum
    models=["qwen3.5:2b"],
    timeout=120,                 # local slow, so adhigam
)
r = local.chat(messages)
print("LOCAL:", r)