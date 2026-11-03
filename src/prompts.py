from pathlib import Path

PROMPT_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(name: str) -> str:
    """name example: 'cv_extract_v1'"""
    return (PROMPT_DIR / f"{name}.txt").read_text(encoding="utf-8")
