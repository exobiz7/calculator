import pytest

from calc.modes import kpi
from calc.modes.kpi import KPI_BY_KEY, KPIS, compute


def _c(key, **values):
    return compute(KPI_BY_KEY[key], values)


def test_representative_values():
    assert _c("roe", net_income=100, equity=500) == pytest.approx(20)
    assert _c("per", price=60000, eps=5000) == pytest.approx(12)
    assert _c("debt_ratio", debt=300, equity=200) == pytest.approx(150)
    assert _c(
        "bep", fixed_cost=1_000_000, price=5000, variable_cost=3000
    ) == pytest.approx(500)
    assert _c("contribution_margin", price=5000, variable_cost=3000) == pytest.approx(
        40
    )
    assert _c("ccc", dso=45, dio=60, dpo=30) == pytest.approx(75)
    assert _c("cagr", begin=100, end=200, years=2) == pytest.approx(41.4213, abs=1e-3)
    assert _c("markup_price", cost=120, markup_rate=25) == pytest.approx(150)
    assert _c("target_margin_price", cost=120, margin_rate=25) == pytest.approx(160)


def test_divide_by_zero_raises():
    with pytest.raises(ValueError):
        _c("per", price=1000, eps=0)


def test_registry_integrity():
    # keys unique, categories valid, every formula uses only its own inputs.
    keys = [k.key for k in KPIS]
    assert len(keys) == len(set(keys)), "duplicate KPI keys"
    for k in KPIS:
        assert k.category in kpi.CATEGORIES, f"{k.key}: bad category"
        # distinct nonzero values so denominators like (price - variable_cost) != 0
        values = {var: float(i + 3) for i, var in enumerate(k.variables)}
        result = compute(k, values)  # must evaluate using only declared variables
        assert isinstance(result, float)


def test_by_category_covers_all():
    counted = sum(len(kpi.by_category(c)) for c in kpi.CATEGORIES)
    assert counted == len(KPIS)
