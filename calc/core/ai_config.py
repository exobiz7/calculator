"""AI provider configuration (stored locally, never committed/logged).

The API key lives only in ~/.calculator/ai_config.json (chmod 600) or an
environment variable — never hardcoded, never written to history.
"""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

_CONFIG_PATH = Path.home() / ".calculator" / "ai_config.json"

# preset -> (provider kind, base_url, default model, env var for key)
PRESETS: dict[str, dict] = {
    "OpenAI": {
        "kind": "openai",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "env": "OPENAI_API_KEY",
    },
    "Gemini": {
        "kind": "openai",  # OpenAI-compatible endpoint
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.5-flash",  # 2.0-flash free tier is quota 0 on many accounts
        "env": "GEMINI_API_KEY",
    },
    "Claude": {
        "kind": "anthropic",
        "base_url": "https://api.anthropic.com",
        "model": "claude-opus-4-8",
        "env": "ANTHROPIC_API_KEY",
    },
    "Ollama (로컬)": {
        "kind": "openai",
        "base_url": "http://localhost:11434/v1",
        "model": "llama3.1",
        "env": "",
    },
    "커스텀 (OpenAI 호환)": {
        "kind": "openai",
        "base_url": "http://localhost:8000/v1",
        "model": "",
        "env": "",
    },
}


@dataclass
class AIConfig:
    preset: str = "OpenAI"
    kind: str = "openai"  # "openai" | "anthropic"
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    api_key: str = ""
    vision: bool = True

    def effective_key(self) -> str:
        """Stored key, else the preset's environment variable."""
        if self.api_key:
            return self.api_key
        env = PRESETS.get(self.preset, {}).get("env", "")
        return os.environ.get(env, "") if env else ""


def from_preset(name: str) -> AIConfig:
    p = PRESETS.get(name, PRESETS["OpenAI"])
    return AIConfig(
        preset=name, kind=p["kind"], base_url=p["base_url"], model=p["model"]
    )


def load() -> AIConfig:
    try:
        data = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
        return AIConfig(**{k: data[k] for k in data if k in AIConfig().__dict__})
    except (FileNotFoundError, ValueError, TypeError):
        return AIConfig()


def save(config: AIConfig, path: Path | None = None) -> None:
    p = path or _CONFIG_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    try:
        p.chmod(0o600)  # key is sensitive — owner-only
    except OSError:
        pass


def masked_key(key: str) -> str:
    if not key:
        return ""
    return (
        key[:3] + "•" * max(0, len(key) - 6) + key[-3:]
        if len(key) > 6
        else "•" * len(key)
    )
