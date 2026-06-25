"""Provider-neutral LLM HTTP client (OpenAI-compatible + Anthropic).

Uses the standard library (urllib) so no provider SDK is required — works with
OpenAI, Gemini's OpenAI-compatible endpoint, local Ollama / LM Studio / vLLM,
and any custom OpenAI-compatible or Anthropic server the user points it at.
"""

import base64
import json
import urllib.request

_ANTHROPIC_VERSION = "2023-06-01"


def _post(url: str, headers: dict, payload: dict, timeout: int) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _data_url(image_bytes: bytes) -> str:
    return "data:image/png;base64," + base64.standard_b64encode(image_bytes).decode()


def chat(
    config,
    system: str,
    user_text: str,
    image_bytes: bytes | None = None,
    timeout: int = 30,
) -> str:
    """Send one chat request; return the model's text. Raises ValueError on failure."""
    key = config.effective_key()
    base = config.base_url.rstrip("/")
    if config.kind == "anthropic":
        content: list = [{"type": "text", "text": user_text}]
        if image_bytes:
            content.insert(
                0,
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": base64.standard_b64encode(image_bytes).decode(),
                    },
                },
            )
        payload = {
            "model": config.model,
            "max_tokens": 1024,
            "system": system,
            "messages": [{"role": "user", "content": content}],
        }
        headers = {
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": _ANTHROPIC_VERSION,
        }
        url = f"{base}/v1/messages"
    else:  # openai-compatible
        user_content: list = [{"type": "text", "text": user_text}]
        if image_bytes:
            user_content.append(
                {"type": "image_url", "image_url": {"url": _data_url(image_bytes)}}
            )
        payload = {
            "model": config.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
        }
        headers = {"content-type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        url = f"{base}/chat/completions"

    try:
        data = _post(url, headers, payload, timeout)
    except Exception as exc:  # network/HTTP/JSON
        raise ValueError(f"API 호출 실패: {exc}") from exc
    return _extract_text(config.kind, data)


def _extract_text(kind: str, data: dict) -> str:
    try:
        if kind == "anthropic":
            parts = data["content"]
            return "".join(p.get("text", "") for p in parts if p.get("type") == "text")
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"응답 형식을 해석할 수 없습니다: {exc}") from exc
