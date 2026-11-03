import re
from dataclasses import dataclass

from pydantic import ValidationError

from src.llm_client import LLMClient
from src.prompts import load_prompt
from src.schema import CVData


@dataclass
class ExtractionResult:
    data: CVData | None
    ok: bool
    repaired: bool          # repair retry venduchaa
    error: str | None
    model: str
    seconds: float
    prompt_tokens: int
    completion_tokens: int
    first_error: str | None = None


def _clean_json(text: str) -> str:
    """Model ```json fences potta, adha eduthudu."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text


def _wrap_cv(cv_text: str) -> str:
    # CV kulla "</cv>" nu ezhudhi tag ah odaika koodadhu
    safe = cv_text.replace("<cv>", "").replace("</cv>", "")
    return f"<cv>\n{safe}\n</cv>"


def extract_cv(client: LLMClient, cv_text: str, version: str = "v1",
               temperature: float = 0.0, seed=None, extra_body=None) -> ExtractionResult:
    system_prompt = load_prompt(f"cv_extract_{version}")
    repair_prompt = load_prompt(f"cv_repair_{version}")

    # Instruction = system message. CV text = user message (veru idam).
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": _wrap_cv(cv_text)},
    ]

    kw = dict(temperature=temperature, seed=seed, extra_body=extra_body)
    r1 = client.chat(messages, **kw)
    seconds = r1.seconds
    ptok, ctok = r1.prompt_tokens, r1.completion_tokens

    # ---- 1st try ----
    try:
        data = CVData.model_validate_json(_clean_json(r1.text))
        return ExtractionResult(data, True, False, None, r1.model,
                                seconds, ptok, ctok)
    except (ValidationError, ValueError) as e:
        first_error = str(e)

    # ---- ONE repair retry ----
    repair_msg = (repair_prompt
                  .replace("{error}", first_error)
                  .replace("{previous_output}", r1.text))
    messages2 = messages + [
        {"role": "assistant", "content": r1.text},
        {"role": "user", "content": repair_msg},
    ]
    r2 = client.chat(messages2, **kw)
    seconds += r2.seconds
    ptok += r2.prompt_tokens
    ctok += r2.completion_tokens

    try:
        data = CVData.model_validate_json(_clean_json(r2.text))
        return ExtractionResult(data, True, True, None, r2.model,
                                seconds, ptok, ctok, first_error)
    except (ValidationError, ValueError) as e:
        return ExtractionResult(None, False, True, str(e), r2.model,
                                seconds, ptok, ctok, first_error)
