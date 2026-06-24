from decimal import Decimal

import pytest

from calc.modes import financial as fin


# --- VAT -------------------------------------------------------------------
def test_add_vat():
    r = fin.add_vat(100000)
    assert r.supply == Decimal("100000")
    assert r.vat == Decimal("10000")
    assert r.total == Decimal("110000")


def test_remove_vat():
    r = fin.remove_vat(110000)
    assert r.supply == Decimal("100000")
    assert r.vat == Decimal("10000")


# --- margin / markup -------------------------------------------------------
def test_sell_from_cost_margin():
    # cost 120, margin 25% (on selling price) -> 160 (benchmark example)
    assert fin.sell_from_cost_margin(120, 25) == Decimal("160")


def test_sell_from_cost_markup():
    assert fin.sell_from_cost_markup(120, 25) == Decimal("150")


def test_margin_and_markup_rate():
    assert fin.margin_rate(120, 160) == pytest.approx(25)
    assert fin.markup_rate(120, 150) == pytest.approx(25)


def test_apply_discount():
    assert fin.apply_discount(50000, 30) == Decimal("35000")


# --- TVM -------------------------------------------------------------------
def test_tvm_fv_basic():
    # 1000 invested (outflow), 5%/yr, 10 yrs -> ~1628.89
    assert fin.tvm_fv(10, 5, pv=-1000, pmt=0) == pytest.approx(1628.894627, rel=1e-6)


def test_tvm_roundtrip_pv():
    fv = fin.tvm_fv(10, 5, pv=-1000, pmt=0)
    assert fin.tvm_pv(10, 5, pmt=0, fv=fv) == pytest.approx(-1000, rel=1e-9)


def test_tvm_pmt_loan():
    # 1,000,000 loan, 0.5%/month, 12 months -> monthly payment ~ -86066
    pmt = fin.tvm_pmt(12, 0.5, pv=1_000_000, fv=0)
    assert pmt == pytest.approx(-86066, abs=1)


def test_tvm_rate_solves():
    # If 1000 grows to 1628.894627 over 10 periods, rate should be ~5%
    rate = fin.tvm_rate(10, pv=-1000, pmt=0, fv=1628.894627)
    assert rate == pytest.approx(5, abs=1e-4)


def test_tvm_n_solves():
    n = fin.tvm_n(5, pv=-1000, pmt=0, fv=1628.894627)
    assert n == pytest.approx(10, abs=1e-6)


# --- amortization ----------------------------------------------------------
def test_amortization_zeroes_balance():
    rows = fin.amortization_schedule(1_000_000, 6, 12)
    assert len(rows) == 12
    assert rows[-1].balance == Decimal("0")
    # Sum of principal repaid equals the original loan.
    total_principal = sum(r.principal for r in rows)
    assert total_principal == Decimal("1000000")


def test_amortization_zero_rate():
    rows = fin.amortization_schedule(1200, 0, 12)
    assert rows[0].payment == Decimal("100")
    assert rows[-1].balance == Decimal("0")
