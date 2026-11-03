import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
c = OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])
for m in c.models.list().data:
    print(m.id)
