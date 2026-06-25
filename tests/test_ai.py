import pytest

from calc.core import ai_config, ai_formula, ai_provider
from calc.core.expr import safe_eval


# --- config ----------------------------------------------------------------
def test_from_preset():
    c = ai_config.from_preset("Claude")
    assert c.kind == "anthropic" and "anthropic.com" in c.base_url


def test_save_load_roundtrip_and_perms(tmp_path):
    p = tmp_path / "ai.json"
    cfg = ai_config.AIConfig(preset="OpenAI", model="gpt-4o-mini", api_key="sk-secret")
    ai_config.save(cfg, path=p)
    assert (p.stat().st_mode & 0o777) == 0o600  # owner-only
    loaded = ai_config.AIConfig(
        **{
            k: v
            for k, v in __import__("json").loads(p.read_text()).items()
            if k in ai_config.AIConfig().__dict__
        }
    )
    assert loaded.api_key == "sk-secret"


def test_effective_key_env_fallback(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    c = ai_config.from_preset("OpenAI")  # no api_key set
    assert c.effective_key() == "env-key"


def test_masked_key():
    assert ai_config.masked_key("sk-abcdef1234") == "sk-" + "•" * 7 + "234"
    assert ai_config.masked_key("") == ""
    assert ai_config.masked_key("abc") == "•••"


# --- provider payload shaping (mock the HTTP _post) ------------------------
def test_openai_payload(monkeypatch):
    captured = {}

    def fake_post(url, headers, payload, timeout):
        captured.update(url=url, headers=headers, payload=payload)
        return {"choices": [{"message": {"content": "hi"}}]}

    monkeypatch.setattr(ai_provider, "_post", fake_post)
    c = ai_config.AIConfig(
        kind="openai", base_url="http://x/v1", model="m", api_key="k"
    )
    assert ai_provider.chat(c, "sys", "hello") == "hi"
    assert captured["url"] == "http://x/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer k"
    assert captured["payload"]["messages"][0]["role"] == "system"


def test_anthropic_payload(monkeypatch):
    captured = {}

    def fake_post(url, headers, payload, timeout):
        captured.update(url=url, headers=headers, payload=payload)
        return {"content": [{"type": "text", "text": "answer"}]}

    monkeypatch.setattr(ai_provider, "_post", fake_post)
    c = ai_config.AIConfig(
        kind="anthropic",
        base_url="https://api.anthropic.com",
        model="claude",
        api_key="k",
    )
    assert ai_provider.chat(c, "sys", "hello") == "answer"
    assert captured["url"].endswith("/v1/messages")
    assert captured["headers"]["x-api-key"] == "k"


# --- formula parsing + safe evaluation ------------------------------------
def test_parse_reply_plain_json():
    f = ai_formula.parse_reply(
        '{"expression":"a/b*100","variables":'
        '[{"name":"a","label":"부분"},{"name":"b","label":"전체"}],'
        '"explanation":"비율"}'
    )
    assert f.expression == "a/b*100"
    assert f.variables[0]["name"] == "a"
    assert safe_eval(f.expression, variables={"a": 1, "b": 4}) == 25


def test_parse_reply_with_code_fence_and_prose():
    reply = 'Sure!\n```json\n{"expression": "x**2", "variables": ["x"]}\n```'
    f = ai_formula.parse_reply(reply)
    assert f.expression == "x**2"
    assert f.variables[0]["name"] == "x"


def test_parse_reply_no_json_raises():
    with pytest.raises(ValueError):
        ai_formula.parse_reply("no json here")


def test_request_formula_uses_provider(monkeypatch):
    monkeypatch.setattr(
        ai_provider,
        "chat",
        lambda *a, **k: (
            '{"expression":"2*r*pi","variables":[{"name":"r","label":"반지름"}]}'
        ),
    )
    f = ai_formula.request_formula(ai_config.AIConfig(), "원 둘레")
    assert safe_eval(f.expression, variables={"r": 1}) == pytest.approx(
        6.283185, abs=1e-5
    )
