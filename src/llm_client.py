import time
import logging
from dataclasses import dataclass

from openai import (
    OpenAI,
    APIConnectionError,   # network issue, timeout kooda idhula varum
    RateLimitError,       # 429
    APIStatusError,       # other HTTP errors
)

log = logging.getLogger(__name__)


class EmptyResponse(Exception):
    pass


@dataclass
class LLMResult:
    text: str
    model: str              # entha model answer kuduthuchu
    prompt_tokens: int
    completion_tokens: int
    seconds: float
    attempts: int           # evlo thadava try pannom


class LLMClient:
    def __init__(self, base_url, api_key, models, timeout=30, max_retries=3):
        # max_retries=0: OpenAI library oda own retry off. Namma retry mattum.
        self.client = OpenAI(
            base_url=base_url, api_key=api_key, timeout=timeout, max_retries=0
        )
        self.models = models
        self.max_retries = max_retries

    @classmethod
    def from_settings(cls, s):
        return cls(s.llm_base_url, s.llm_api_key, s.models,
                   s.llm_timeout, s.llm_max_retries)

    @staticmethod
    def _is_retryable(err) -> bool:
        if isinstance(err, (APIConnectionError, RateLimitError, EmptyResponse)):
            return True
        if isinstance(err, APIStatusError) and err.status_code >= 500:
            return True
        return False   # 400, 401, 404 maari: retry panni payan illa

    def chat(self, messages, temperature=0.0, seed=None, extra_body=None):
        errors = []
        total_attempts = 0

        for model in self.models:
            for attempt in range(1, self.max_retries + 1):
                total_attempts += 1
                try:
                    kwargs = dict(model=model, messages=messages,
                                  temperature=temperature)
                    if seed is not None:
                        kwargs["seed"] = seed
                    if extra_body:
                        kwargs["extra_body"] = extra_body

                    start = time.perf_counter()
                    resp = self.client.chat.completions.create(**kwargs)
                    seconds = time.perf_counter() - start

                    if not (resp.choices[0].message.content or "").strip():
                        raise EmptyResponse("model returned empty text")
                    usage = resp.usage
                    return LLMResult(
                        text=resp.choices[0].message.content or "",
                        model=model,
                        prompt_tokens=usage.prompt_tokens if usage else 0,
                        completion_tokens=usage.completion_tokens if usage else 0,
                        seconds=seconds,
                        attempts=total_attempts,
                    )
                except Exception as e:
                    errors.append(f"{model} attempt {attempt}: {type(e).__name__}: {e}")
                    log.warning(errors[-1])
                    if not self._is_retryable(e):
                        break                      # indha model vendaam, next model
                    if attempt < self.max_retries:
                        time.sleep(2 ** (attempt - 1))   # 1s, 2s, 4s

        raise RuntimeError("Ellā models um fail:\n" + "\n".join(errors))