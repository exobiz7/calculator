import pytest

from calc.core import forex

RATES = {"EUR": 1.0, "USD": 1.1, "KRW": 1500.0, "JPY": 160.0}


def test_convert_math():
    assert forex._convert(1, "EUR", "USD", RATES) == pytest.approx(1.1)
    assert forex._convert(1, "USD", "KRW", RATES) == pytest.approx(1500 / 1.1)
    assert forex._convert(10, "KRW", "KRW", RATES) == pytest.approx(10)


def test_convert_unknown_currency():
    with pytest.raises(ValueError):
        forex._convert(1, "USD", "XXX", RATES)


def test_disk_cache_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(forex, "_CACHE_PATH", tmp_path / "fx.json")
    cache = {"date": "2026-06-24", "fetched_at": "t", "rates": RATES}
    forex._save_disk(cache)
    assert forex._load_disk() == cache


def test_ensure_rates_uses_disk_without_network(tmp_path, monkeypatch):
    monkeypatch.setattr(forex, "_CACHE_PATH", tmp_path / "fx.json")
    monkeypatch.setattr(forex, "_cache", None)
    forex._save_disk({"date": "2026-06-24", "fetched_at": "t", "rates": RATES})

    def _boom(*a, **k):
        raise AssertionError("network should not be called when disk cache exists")

    monkeypatch.setattr(forex, "refresh", _boom)
    rates = forex.ensure_rates()["rates"]
    assert forex._convert(1, "USD", "KRW", rates) == pytest.approx(1500 / 1.1)
