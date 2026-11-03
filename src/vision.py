import base64
import io
import re
from pathlib import Path

import pymupdf as fitz
from PIL import Image
from pydantic import ValidationError

from src.llm_client import LLMClient
from src.prompts import load_prompt
from src.schema import InvoiceData

MAX_BYTES = 5 * 1024 * 1024
MAX_SIDE = 1000
ALLOWED = {".png", ".jpg", ".jpeg", ".pdf"}


def load_untrusted_image(path: str) -> bytes:
    """File ah nambaadhe: type, size check, then clean PNG ah maathu."""
    p = Path(path)
    if p.suffix.lower() not in ALLOWED:
        raise ValueError(f"file type not allowed: {p.suffix}")
    if p.stat().st_size > MAX_BYTES:
        raise ValueError("file too large")

    raw = p.read_bytes()
    if p.suffix.lower() == ".pdf":
        if not raw.startswith(b"%PDF"):
            raise ValueError("not a real PDF")
        doc = fitz.open(stream=raw, filetype="pdf")
        if doc.page_count < 1:
            raise ValueError("empty PDF")
        pix = doc[0].get_pixmap(dpi=100)      # first page mattum
        img = Image.open(io.BytesIO(pix.tobytes("png")))
    else:
        img = Image.open(io.BytesIO(raw))
        img.verify()                          # fake image na error
        img = Image.open(io.BytesIO(raw))

    img = img.convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    out = io.BytesIO()
    img.save(out, format="PNG")               # metadata ellam pogum
    return out.getvalue()


def _clean_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    return re.sub(r"\s*```$", "", text)


def extract_invoice(client: LLMClient, path: str, extra_body=None):
    png = load_untrusted_image(path)
    b64 = base64.b64encode(png).decode()
    messages = [
        {"role": "system", "content": load_prompt("invoice_extract_v1")},
        {"role": "user", "content": [
            {"type": "text", "text": "Extract the invoice fields from this image."},
            {"type": "image_url",
             "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ]},
    ]
    r = client.chat(messages, temperature=0.0, extra_body=extra_body)
    try:
        data = InvoiceData.model_validate_json(_clean_json(r.text))
    except (ValidationError, ValueError) as e:
        return None, r, f"validation failed: {e}"

    # total ah line items kooda cross-check pannu (injection pidikka)
    amounts = [i.amount for i in data.line_items if i.amount is not None]
    note = None
    if data.total is not None and amounts and abs(sum(amounts) - data.total) > 0.01:
        note = f"WARNING: total {data.total} != sum of items {sum(amounts)}"
    return data, r, note
