"""Live currency exchange via the Frankfurter API (ECB reference rates).

Free, unlimited, no API key (https://frankfurter.dev) — daily ECB rates, ~30
fiat currencies. Rates are cached to disk so conversion keeps working offline
with the last-known values. Networking uses the standard library (urllib).
"""

import json
import urllib.request
from datetime import datetime
from pathlib import Path

API = "https://api.frankfurter.dev/v1"
BASE = "EUR"  # ECB base; all rates stored relative to EUR (EUR = 1.0)
_CACHE_PATH = Path.home() / ".calculator" / "forex_cache.json"
_TIMEOUT = 10

_cache: dict | None = None  # {"date", "fetched_at", "rates": {code: per-EUR}}
_currencies: dict | None = None  # {code: name}


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "calculator/1.0"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


# --- rates ----------------------------------------------------------------
def refresh() -> dict:
    """Fetch fresh rates from the API; update memory + disk cache. Raises on failure."""
    global _cache
    data = _get_json(f"{API}/latest?base={BASE}")
    rates = dict(data.get("rates", {}))
    rates[BASE] = 1.0
    _cache = {
        "date": data.get("date", ""),
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "rates": rates,
    }
    _save_disk(_cache)
    return _cache


def _save_disk(cache: dict) -> None:
    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def _load_disk() -> dict | None:
    try:
        return json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return None


def ensure_rates() -> dict:
    """Return cached rates, loading disk or fetching if needed. Raises if no source."""
    global _cache
    if _cache is None:
        _cache = _load_disk()
    if _cache is None:
        refresh()  # first run with no cache -> must hit network
    return _cache


def _convert(amount: float, frm: str, to: str, rates: dict) -> float:
    """Pure conversion given per-base rates (EUR=1)."""
    if frm not in rates:
        raise ValueError(f"알 수 없는 통화: {frm}")
    if to not in rates:
        raise ValueError(f"알 수 없는 통화: {to}")
    return amount * rates[to] / rates[frm]


def convert(amount: float, frm: str, to: str) -> float:
    return _convert(amount, frm, to, ensure_rates()["rates"])


def codes() -> list[str]:
    return sorted(ensure_rates()["rates"].keys())


def cached_codes() -> list[str]:
    """Currency codes from cache only (no network). [] if nothing cached yet."""
    c = _cache or _load_disk()
    return sorted(c["rates"].keys()) if c else []


def info() -> tuple[str, str]:
    """(rate date, fetched_at) of the cached rates, or ('', '')."""
    c = _cache or _load_disk()
    return (c.get("date", ""), c.get("fetched_at", "")) if c else ("", "")


# --- currency names (optional, for nicer labels) --------------------------
def currencies() -> dict:
    """{code: name}; cached. Falls back to codes-only on failure."""
    global _currencies
    if _currencies is None:
        try:
            _currencies = _get_json(f"{API}/currencies")
        except Exception:
            _currencies = {}
    return _currencies
