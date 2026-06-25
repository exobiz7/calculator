"""Turn a natural-language / formula / LaTeX / image request into a formula.

The model only *proposes* a formula string in our expr syntax plus a variable
list; evaluation always goes through safe_eval (ast whitelist) — the model's
output is never executed.
"""

import json
import re
from dataclasses import dataclass, field

from calc.core import ai_provider

SYSTEM = (
    "You convert a math request into a reusable formula. "
    "Respond with ONLY a JSON object, no prose, no code fences:\n"
    '{"expression": "<formula using + - * / ** and functions like sin, cos, '
    "tan, asin, acos, atan, sinh, cosh, tanh, log (base10), ln, exp, sqrt, "
    'abs, fact, nPr, nCr, gcd, lcm, hypot, logb(x,base) and constants pi, e>", '
    '"variables": [{"name": "<identifier used in expression>", "label": "<short human label>"}], '
    '"explanation": "<one short sentence>"}\n'
    "Rules: use ^ only as **; multiplication must be explicit (2*x not 2x); "
    "variable names are plain identifiers (letters/digits/underscore); put every "
    "unknown quantity in variables; if the input is already a formula or LaTeX, "
    "convert it to this syntax."
)


@dataclass
class AIFormula:
    expression: str
    variables: list[dict] = field(default_factory=list)
    explanation: str = ""


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of the model's reply."""
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError("모델 응답에서 JSON을 찾지 못했습니다")
    try:
        return json.loads(m.group(0))
    except ValueError as exc:
        raise ValueError(f"JSON 파싱 실패: {exc}") from exc


def parse_reply(text: str) -> AIFormula:
    data = _extract_json(text)
    expr = str(data.get("expression", "")).strip()
    if not expr:
        raise ValueError("식을 생성하지 못했습니다")
    variables = []
    for v in data.get("variables", []) or []:
        if isinstance(v, dict) and v.get("name"):
            variables.append(
                {"name": str(v["name"]), "label": str(v.get("label", v["name"]))}
            )
        elif isinstance(v, str):
            variables.append({"name": v, "label": v})
    return AIFormula(expr, variables, str(data.get("explanation", "")))


def request_formula(
    config, prompt: str, image_bytes: bytes | None = None, timeout: int = 30
) -> AIFormula:
    """Ask the configured model for a formula; returns a parsed AIFormula."""
    if not prompt.strip() and image_bytes is None:
        raise ValueError("입력이 비어 있습니다")
    reply = ai_provider.chat(
        config,
        SYSTEM,
        prompt or "Read the formula in the image.",
        image_bytes=image_bytes,
        timeout=timeout,
    )
    return parse_reply(reply)
